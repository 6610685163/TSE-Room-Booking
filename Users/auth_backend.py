"""
TU REST API Authentication Backend
Requirement: FR-AUTH-02, FR-AUTH-03
Authenticates users against Thammasat University's REST API
"""

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
    
    TU_API_ENDPOINT = 'https://restapi.tu.ac.th/api/v1/auth/Ad/verify'
    
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
        if not self._verify_tu_credentials(username, password):
            logger.warning(f"TU REST API authentication failed for user: {username}")
            return None
        
        # Step 2: Get or create user in local database
        try:
            user_profile = UserProfile.objects.get(tu_username=username)
            user = user_profile.user
            
            # Update user info
            user.is_active = True
            user.save()
            logger.info(f"User {username} authenticated successfully")
            return user
            
        except UserProfile.DoesNotExist:
            # First time login - create user
            logger.info(f"Creating new user profile for {username}")
            try:
                # Create Django User
                user = User.objects.create_user(
                    username=username,
                    email=f"{username}@thammasat.ac.th"
                )
                
                # Create UserProfile (role will be set by admin later)
                UserProfile.objects.create(
                    user=user,
                    tu_username=username,
                    full_name=username,
                    email=f"{username}@thammasat.ac.th",
                    role='lecturer'  # Default role
                )
                
                logger.info(f"New user profile created for {username}")
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
            True if credentials are valid, False otherwise
        """
        try:
            # Get Application-Key from settings
            application_key = settings.TU_API_KEY
            if not application_key:
                logger.error("TU_API_KEY not configured in settings")
                return False
            
            # Prepare request
            headers = {
                'Content-Type': 'application/json',
                'Application-Key': application_key
            }
            
            payload = {
                'UserName': username,
                'PassWord': password
            }
            
            # Send request to TU REST API
            response = requests.post(
                self.TU_API_ENDPOINT,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            # Check response
            if response.status_code == 200:
                response_data = response.json()
                # TU API returns success when status is 1 or similar
                if response_data.get('status') == 1 or response_data.get('valid'):
                    logger.info(f"TU REST API verification successful for {username}")
                    return True
                else:
                    logger.warning(f"TU REST API returned invalid status for {username}")
                    return False
            else:
                logger.warning(
                    f"TU REST API returned status {response.status_code} for {username}"
                )
                return False
                
        except requests.exceptions.Timeout:
            logger.error("TU REST API request timeout")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"TU REST API request error: {str(e)}")
            return False
        except json.JSONDecodeError:
            logger.error("Failed to parse TU REST API response")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during TU authentication: {str(e)}")
            return False
    
    def get_user(self, user_id):
        """
        Get user by ID
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
