import requests
import json
import logging
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import UserProfile

User = get_user_model()
logger = logging.getLogger(__name__)


class TURestAPIBackend(ModelBackend):
    """
    Custom authentication backend for TU REST API
    Authenticates against https://restapi.tu.ac.th/api/v1/auth/Ad/verify
    """

    TU_API_ENDPOINT = "https://restapi.tu.ac.th/api/v1/auth/Ad/verify"

    def authenticate(self, request, username=None, password=None):
        """
        Authenticate user against TU REST API

        Args:
            request: HTTP request object
            username: TU username
            password: TU password

        Returns:
            User object if authentication successful, None otherwise

        Requirement: FR-AUTH-01, FR-AUTH-02
        """
        if not username or not password:
            return None

        # Step 1: Verify credentials with TU REST API
        is_valid, user_data = self._verify_tu_credentials(username, password)

        if not is_valid:
            logger.warning(f"TU REST API authentication failed for user: {username}")
            return None

        # ดึง Email และ ชื่อ-นามสกุล จริงจาก API (ใช้ค่า fallback ป้องกัน error)
        api_email = f"{username}@thammasat.ac.th"
        api_full_name = username

        if user_data:
            api_email = user_data.get("Email", api_email)# ถ้า API ส่งข้อมูล (data) กลับมาจริง
            # ระบบจะไปหยิบค่าจาก Key ที่ชื่อ 'Email' ใน API มาทับค่าสำรองทันที
            first_name = user_data.get("First_Name_Th", "")
            last_name = user_data.get("Last_Name_Th", "")
            if first_name or last_name:
                api_full_name = f"{first_name} {last_name}".strip()

        # Step 2: Get or create user in local database
        try:
            user_profile = UserProfile.objects.get(tu_username=username)
            user = user_profile.user

            # Update user info ด้วยข้อมูลล่าสุดจาก API เสมอ
            user.email = api_email
            user.is_active = True
            user.save()

            user_profile.full_name = api_full_name
            user_profile.email = api_email
            user_profile.save()

            logger.info(f"User {username} authenticated successfully")
            return user

        except UserProfile.DoesNotExist:
            # First time login - create user
            logger.info(f"Creating new user profile for {username}")
            try:
                # Create Django User
                user = User.objects.create_user(username=username, email=api_email)

                # Create UserProfile (role will be set by admin later)
                UserProfile.objects.create(
                    user=user,
                    tu_username=username,
                    full_name=api_full_name,
                    email=api_email,
                    role="lecturer",  # Default role
                )

                logger.info(
                    f"New user profile created for {username} with real email {api_email}"
                )
                return user

            except Exception as e:
                logger.error(f"Error creating user profile for {username}: {str(e)}")
                return None

    def _verify_tu_credentials(self, username, password):
        """
        Verify credentials against TU REST API
        Requirement: FR-AUTH-02

        Args:
            username: TU username
            password: TU password

        Returns:
            Tuple (True/False, Dict/None) containing validation status and user data
        """
        try:
            # Get Application-Key from settings
            application_key = settings.TU_API_KEY
            if not application_key:
                logger.error("TU_API_KEY not configured in settings")
                return False, None

            # Prepare request
            headers = {
                "Content-Type": "application/json",
                "Application-Key": application_key,
            }

            payload = {"UserName": username, "PassWord": password}

            # Send request to TU REST API
            response = requests.post(
                self.TU_API_ENDPOINT, json=payload, headers=headers, timeout=10
            )

            # Check response
            if response.status_code == 200:
                response_data = response.json()
                # TU API returns success when status is 1 or similar
                if response_data.get("status") in [1, True] or response_data.get(
                    "valid"
                ):
                    logger.info(f"TU REST API verification successful for {username}")

                    # แกะก้อนข้อมูล data ออกมาจาก JSON Response
                    user_data = None
                    data_list = response_data.get("data", [])
                    if data_list and isinstance(data_list, list):
                        user_data = data_list[0]

                    return True, user_data
                else:
                    logger.warning(
                        f"TU REST API returned invalid status for {username}"
                    )
                    return False, None
            else:
                logger.warning(
                    f"TU REST API returned status {response.status_code} for {username}"
                )
                return False, None

        except requests.exceptions.Timeout:
            logger.error("TU REST API request timeout")
            return False, None
        except requests.exceptions.RequestException as e:
            logger.error(f"TU REST API request error: {str(e)}")
            return False, None
        except json.JSONDecodeError:
            logger.error("Failed to parse TU REST API response")
            return False, None
        except Exception as e:
            logger.error(f"Unexpected error during TU authentication: {str(e)}")
            return False, None

    def get_user(self, user_id):
        """
        Get user by ID
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
