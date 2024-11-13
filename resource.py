# importing all module
from flask_restful import Resource
import logging

from werkzeug.utils import secure_filename

logging.basicConfig ( level=logging.INFO )  # You can set it to DEBUG for more detailed logs
from flask import Flask, render_template, make_response, redirect, url_for, flash, session, request, jsonify, app
from model import db, User, Post, Profile, Like, Comment
from config import config
import flask_restful
from werkzeug.security import generate_password_hash, check_password_hash
import os
import time
import base64
from flask import current_app


class Home ( Resource ):
    def get(self):
        return make_response ( render_template ( 'index.html' ) )


class Register ( Resource ):
    def get(self):
        return make_response ( render_template ( "register.html" ) )

    def post(self):
        data = flask_restful.request.form

        # Validate form data
        if not self.is_valid_form_data ( data ):
            flash ( "Missing required fields", "danger" )
            return redirect ( url_for ( 'register' ) ), 400

        username = data["username"]
        email = data["email"]
        password = data["password"]
        number = data.get ( "number" )

        # Check if the user already exists
        if self.user_exists ( username, email, number ):
            flash ( "User already exists", "danger" )
            return redirect ( url_for ( 'register' ) ), 409

        # Create and save the new user
        try:
            self.create_new_user ( email, username, password, number )
            flash ( 'Registration successful! Please log in.', 'success' )
            return redirect ( url_for ( 'login' ) )
        except Exception as e:
            db.session.rollback ()
            flash ( f"An error occurred: {str ( e )}", 'danger' )
            return redirect ( url_for ( 'register' ) ), 500

    def is_valid_form_data(self, data):
        """Helper function to check if required form fields are present"""
        required_fields = ['username', 'password', 'email']
        return all ( key in data for key in required_fields )

    def user_exists(self, username, email, number):
        """Helper function to check if a user already exists"""
        return User.query.filter (
            (User.email == email) | (User.username == username) | (User.number == number)
        ).first ()

    def create_new_user(self, email, username, password, number):
        """Helper function to create and commit a new user to the database"""
        hashed_password = generate_password_hash ( password )
        new_user = User ( email=email, username=username, password=hashed_password, number=number )
        db.session.add ( new_user )
        db.session.commit ()


class Login ( Resource ):
    """
    Handles user login functionality (GET and POST).
    """

    def get(self):
        """
        Renders the login page.
        """
        return make_response ( render_template ( "login.html" ) )

    def post(self):
        """
        Authenticates user based on email and password.
        """
        data = flask_restful.request.form

        # Validate form data
        if not self.is_valid_form_data ( data ):
            flash ( "Missing required fields", "danger" )
            return redirect ( url_for ( "login" ) ), 400

        email = data["email"]
        password = data["password"]

        # Retrieve user and validate credentials
        user = self.get_user_by_email ( email )
        if not user:
            flash ( "User not found", "danger" )
            return redirect ( url_for ( "login" ) ), 404

        if not self.verify_password ( user.password, password ):
            flash ( "Invalid credentials", "danger" )
            return redirect ( url_for ( "login" ) ), 401

        # Successful login
        self.create_user_session ( user )
        flash ( "Login successful!", "success" )
        return redirect ( url_for ( "dashboard" ) )

    def is_valid_form_data(self, data):
        """
        Checks if the required form fields are present.
        """
        return all ( key in data for key in ['email', 'password'] )

    def get_user_by_email(self, email):
        """
        Fetches user by email.
        """
        return User.query.filter_by ( email=email ).first ()

    def verify_password(self, stored_password, provided_password):
        """
        Verifies if the provided password matches the stored password.
        """
        return check_password_hash ( stored_password, provided_password )

    def create_user_session(self, user):
        """
        Sets the user session after successful login.
        """
        session['User_id'] = user.id
        # ForgotPassword  Resource


class ForgotPassword ( Resource ):
    """
    Handles the Forgot Password functionality (GET and POST).
    """

    def get(self):
        """
        Renders the forgot password page.
        """
        return make_response ( render_template ( "forgot_password.html" ) )

    def post(self):
        """
        Handles the form submission for password reset request.
        """
        email = flask_restful.request.form.get ( "email" )

        # Check if the email exists in the database
        user = self.get_user_by_email ( email )
        if user:
            # Redirect to the reset password page with the email
            return self.redirect_to_reset_password ( email )

        flash ( 'Email not found.', 'danger' )
        return redirect ( url_for ( 'forgotpassword' ) )

    def get_user_by_email(self, email):
        """
        Retrieves a user by their email address.
        """
        return User.query.filter_by ( email=email ).first ()

    def redirect_to_reset_password(self, email):
        """
        Redirects to the reset password page with the provided email.
        """
        return redirect ( url_for ( 'resetpassword', email=email ) )

        # ResetPassword Resource


class ResetPassword ( Resource ):
    """
    Handles the Reset Password functionality (GET and POST).
    """

    def get(self):
        """
        Renders the reset password page with the user's email as a parameter.
        """
        email = flask_restful.request.args.get ( 'email' )
        return make_response ( render_template ( "reset_password.html", email=email ) )

    def post(self):
        """
        Handles the form submission for resetting the password.
        """
        email = flask_restful.request.form.get ( "email" )
        new_password = flask_restful.request.form.get ( "new_password" )

        # Attempt to reset the user's password
        if self.reset_user_password ( email, new_password ):
            flash ( 'Your password has been reset successfully!', 'success' )
            return redirect ( url_for ( 'login' ) )

        flash ( 'User not found.', 'danger' )
        return redirect ( url_for ( 'forgotpassword' ) )

    def reset_user_password(self, email, new_password):
        """
        Resets the user's password by updating the hash of the new password.
        """
        user = self.get_user_by_email ( email )
        if user:
            user.password = generate_password_hash ( new_password )
            db.session.commit ()
            return True
        return False

    def get_user_by_email(self, email):
        """
        Retrieves a user by their email address.
        """
        return User.query.filter_by ( email=email ).first ()


class Dashboard ( Resource ):
    """
    Displays the dashboard, including user posts, profiles, and user details.
    """

    def get(self):
        """
        Retrieves and displays the dashboard, including posts, profiles, and the current user's information.
        Redirects to login if the user is not authenticated.
        """
        current_user_id = self.get_current_user_id ()

        # Redirect to login if user is not authenticated
        if current_user_id is None:
            return self.redirect_to_login ()

        # Fetch the necessary data for the dashboard
        users = self.get_all_users ()
        posts = self.get_recent_posts ()
        profiles = self.get_all_profiles ()
        user = self.get_user_by_id ( current_user_id )
        profile = self.get_profile_by_user_id ( current_user_id )
        comments = self.get_all_comments()

        # Render the dashboard page
        return self.render_dashboard ( posts, profile, profiles, current_user_id, user, users,comments )

    def get_current_user_id(self):
        """
        Retrieves the current logged-in user's ID from the session.
        """
        return session.get ( 'User_id' )

    def redirect_to_login(self):
        """
        Redirects the user to the login page.
        """
        return redirect ( url_for ( 'login' ) )

    def get_all_users(self):
        """
        Fetches all users from the database.
        """
        return User.query.all ()

    def get_recent_posts(self):
        """
        Fetches the most recent posts, ordered by post ID in descending order.
        """
        return Post.query.order_by ( Post.id.desc () ).all ()

    def get_all_profiles(self,user_id=None):
        """
        Fetches all profiles from the database.
        """
        return Profile.query.filter_by(user_id=user_id).first()

    def get_all_comments(self,post_id=None):
        """
        Fetches all comments from the database.
        """
        return  Comment.query.filter_by(post_id=post_id).all()

    def get_user_by_id(self, user_id):
        """
        Fetches a user from the database by their ID.
        """
        return User.query.get ( user_id )

    def get_profile_by_user_id(self,user_id=None):
        """
        Fetches the profile associated with a specific user by user ID.
        """
        return Profile.query.filter_by (user_id=user_id).all ()

    def render_dashboard(self, posts, profile, profiles, current_user_id, user, users,comments):
        """
        Renders the dashboard page with the provided data.
        """
        return make_response ( render_template (
            'dashboard.html',
            posts=posts,
            profile=profile,
            profiles=profiles,
            current_user_id=current_user_id,
            user=user,
            users=users,
            comments=comments
        ) )


class Add_Post ( Resource ):
    """
    Handles the logic for adding, editing, and deleting posts.
    """

    def get(self, post_id=None):
        """
        Renders the form for adding or editing a post.
        """
        if post_id is None:
            return self.render_new_post_form ()
        else:
            return self.render_edit_post_form ( post_id )

    def render_new_post_form(self):
        """
        Renders the form for adding a new post.
        """
        return make_response ( render_template ( 'add_post.html', post=None ) )

    def render_edit_post_form(self, post_id):
        """
        Renders the form for editing an existing post.
        """
        post = Post.query.get_or_404 ( post_id )
        return make_response ( render_template ( 'add_post.html', post=post ) )

    def post(self):
        """
        Handles form submission for adding or editing a post.
        """
        title = request.form.get ( 'title' )
        content = request.form.get ( 'content' )
        user_id = session.get ( 'User_id' )
        filtered_image_data = request.form.get ( 'filtered_image' )

        # Ensure the user is logged in
        if not user_id:
            flash ( "User ID is required.", 'danger' )
            return redirect ( url_for ( 'add_post' ) )

        # Handle image processing
        image_path = self.handle_image_upload ( filtered_image_data )

        if not image_path:
            return redirect ( url_for ( 'add_post' ) )

        # Create and save the new post
        return self.create_post ( title, content, user_id, image_path )

    # Assuming you're passing 'filtered_image_data' containing base64-encoded image data
    def handle_image_upload(self, filtered_image_data):
        app = current_app  # Access current app instance
        logging.debug ( f"Flask Config: {app.config}" )  # Log the entire config dictionary

        if filtered_image_data:
            try:
                # Split the header and the base64-encoded image data
                header, encoded = filtered_image_data.split ( ',', 1 )

                # Extract the file extension from the MIME type (e.g., image/jpeg, image/png)
                file_extension = header.split ( ';' )[0].split ( '/' )[1]

                # Check for allowed image formats
                if file_extension not in ['jpg', 'jpeg', 'png', 'gif']:
                    flash ( "Unsupported image format. Please upload jpg, jpeg, png, or gif.", 'danger' )
                    return None

                # Generate a filename for the uploaded image
                image_filename = f"{session.get ( 'User_id' )}_post_image_{int ( time.time () )}.{file_extension}"
                image_path = os.path.join ( app.config['UPLOAD_FOLDER'], secure_filename ( image_filename ) )

                # Ensure the upload directory exists
                if not os.path.exists ( app.config['UPLOAD_FOLDER'] ):
                    os.makedirs ( app.config['UPLOAD_FOLDER'] )  # Create the directory if it doesn't exist

                # Decode the base64 image and save it to the disk
                with open ( image_path, "wb" ) as f:
                    f.write ( base64.b64decode ( encoded.strip () ) )  # Strip any unwanted whitespace

                # Return the relative path to save in the DB
                return 'uploads/' + image_filename
            except Exception as e:
                flash ( f"Image processing failed: {str ( e )}", 'danger' )
                return None
        else:
            flash ( "No image data provided.", 'danger' )
            return None

    def create_post(self, title, content, user_id, image_path):
        """
        Creates a new post in the database and commits it.
        """
        try:
            new_post = Post (
                image_path=image_path,
                title=title,
                content=content,
                user_id=user_id,
                likes_count=0
            )
            db.session.add ( new_post )

            # Update the user's post count
            user = User.query.get ( user_id )
            if user:
                user.post_count += 1

            db.session.commit ()
            flash ( 'Post added successfully!', 'success' )
            return redirect ( url_for ( 'dashboard' ) )
        except Exception as e:
            db.session.rollback ()
            flash ( f"An error occurred: {str ( e )}", 'danger' )
            return redirect ( url_for ( 'add_post' ) )

    def delete(self, post_id):
        """
        Handles the deletion of a post.
        """
        post = Post.query.get_or_404 ( post_id )

        try:
            db.session.delete ( post )

            # Update the user's post count
            user = User.query.get ( post.user_id )
            if user:
                user.post_count -= 1

            db.session.commit ()
            flash ( 'Post deleted successfully!', 'success' )
            return redirect ( url_for ( 'dashboard' ) )
        except Exception as e:
            db.session.rollback ()
            flash ( f"An error occurred while deleting the post: {str ( e )}", 'danger' )
            return redirect ( url_for ( 'dashboard' ) )

class UpdateProfile ( Resource ):
    """
    Handles the logic for updating a user's profile information.
    """

    def get(self, profile_id=None):
        """
        Renders the form for updating the profile.
        If `profile_id` is provided, it fetches the existing profile to edit.
        """
        if profile_id is None:
            return self.render_new_profile_form ()
        else:
            return self.render_edit_profile_form ( profile_id )

    def render_new_profile_form(self):
        """
        Renders the form for creating a new profile.
        """
        return make_response ( render_template ( 'update_profile.html', profile=None ) )

    def render_edit_profile_form(self, profile_id):
        """
        Renders the form for editing an existing profile.
        """
        profile = Profile.query.get_or_404 ( profile_id )
        users = User.query.all ()
        return make_response ( render_template ( 'update_profile.html', profile=profile, users=users ) )

    def post(self):
        """
        Handles form submission to update a user's profile information,
        including bio, nickname, and image upload.
        """
        user_id = session.get ( 'User_id' )
        print ( f"User ID from session: {user_id}" )  # Debugging step

        # Ensure the user is logged in
        if not user_id:
            flash ( "You need to log in to update your profile.", 'danger' )
            return redirect ( url_for ( 'login' ) )  # Redirect to login page

        # Fetch the user object
        user = User.query.get ( user_id )
        if not user:
            flash ( "User not found.", 'danger' )
            return redirect ( url_for ( 'dashboard' ) )  # Redirect to dashboard or another page

        # Fetch the Profile or create one if it doesn't exist
        profile = Profile.query.filter_by ( user_id=user_id ).first ()
        if not profile:
            profile = self.create_new_profile ( user_id )

        # Update the profile with the submitted data
        return self.update_profile ( profile, user )

    def create_new_profile(self, user_id):
        """
        Creates a new profile for the user if none exists.
        """
        new_profile = Profile ( user_id=user_id, bio='', nickname='', image_path='' )
        db.session.add ( new_profile )
        db.session.commit ()  # Commit to generate an ID for the profile
        return new_profile

    def update_profile(self, profile, user):
        """
        Updates the profile fields: bio, nickname, and image path.
        """
        try:
            bio = request.form['bio']
            nickname = request.form['nickname']
            image = request.files.get ( 'image' )

            # Handle image upload
            image_path = self.handle_image_upload ( image, profile )

            # Update Profile fields
            profile.nickname = nickname
            profile.bio = bio
            profile.image_path = image_path  # Update image path

            # Update the username in the profile (optional if needed)
            profile.username = user.username  # Assuming you have a username field in Profile

            # Commit changes to the database
            db.session.commit ()
            flash ( 'Profile updated successfully!', 'success' )
            return redirect ( url_for ( 'dashboard' ) )

        except Exception as e:
            db.session.rollback ()
            flash ( f"An error occurred: {e}", 'danger' )
            return redirect ( url_for ( 'updateprofile' ) )

    def handle_image_upload(self, image, profile):
        """
        Handles the image upload logic and returns the path of the uploaded image.
        If no image is uploaded, it retains the existing image path.
        """
        if image:
            image_path = os.path.join ( app.config['UPLOAD_FOLDER'], image.filename )
            image.save ( image_path )
            return 'uploads/' + image.filename
        else:
            return profile.image_path  # Keep the existing image path if no new image is uploaded
class profile ( Resource ):
    """
    Handles the logic for displaying a user's profile page.
    """

    def get(self, User_id=None):
        """
        Renders the profile page for the current user or a specified user.

        If `User_id` is provided, displays that user's profile. Otherwise, displays the current user's profile.
        """
        current_user_id = self.get_user_id ( User_id )

        if not current_user_id:
            flash ( "Please log in to view your profile.", 'warning' )
            return redirect ( url_for ( 'login' ) )

        # Fetch the necessary data
        user, profile, posts, profiles = self.fetch_user_data ( current_user_id )

        # Render the profile page
        return self.render_profile_page ( user, profile, posts, profiles, current_user_id )

    def get_user_id(self, User_id):
        """
        Determines the user ID to be used for fetching the profile.
        If `User_id` is provided, return that. Otherwise, use the current session's user ID.
        """
        if User_id is None:
            return session.get ( 'User_id' )  # Get user ID from session if available
        return User_id  # Use provided User_id if available

    def fetch_user_data(self, current_user_id):
        """
        Fetches the necessary data for the user, profile, posts, and profiles.

        Returns:
            - user: The User object for the given user ID.
            - profile: The Profile object for the given user ID.
            - posts: List of posts ordered by the most recent first.
            - profiles: List of all profiles (can be modified based on requirements).
        """
        user = User.query.get ( current_user_id )
        if not user:
            flash ( "User not found.", 'danger' )
            return redirect ( url_for ( 'login' ) )

        # Fetch user profile, posts, and other related data
        profile = Profile.query.filter_by ( user_id=current_user_id ).all ()
        posts = Post.query.order_by ( Post.id.desc () ).all ()
        profiles = Profile.query.all ()

        return user, profile, posts, profiles

    def render_profile_page(self, user, profile, posts, profiles, current_user_id):
        """
        Renders the profile page using the fetched data.

        Args:
            user: The User object for the current user.
            profile: The Profile object for the current user.
            posts: List of posts by the user.
            profiles: List of all profiles (optional, could be used for other functionality).
            current_user_id: The current user's ID.

        Returns:
            A rendered template with the provided data.
        """
        return make_response ( render_template (
            'Profile.html',
            posts=posts,
            profile=profile,
            current_user_id=current_user_id,
            user=user,
            profiles=profiles
        ) )


class LikePost ( Resource ):
    """


    Handles the logic for liking and unliking a post.
    """

    def post(self, post_id):
        """
        Likes or unlikes a post based on the current user's action.

        Args:
            post_id (int): The ID of the post to like/unlike.

        Returns:
            JSON response with success status and updated like count.
        """
        user_id = self.get_user_id ()

        if not user_id:
            return self.create_error_response ( "User not logged in", 403 )

        post = self.get_post ( post_id )
        if not post:
            return self.create_error_response ( "Post not found", 404 )

        success, message = self.toggle_like ( user_id, post )
        if not success:
            return self.create_error_response ( message, 400 )

        db.session.commit ()  # Commit the changes to the database

        return jsonify ( {"success": True, "new_like_count": post.likes_count} )

    def get_user_id(self):
        """
        Retrieves the user ID from the session.

        Returns:
            int or None: The user ID if logged in, otherwise None.
        """
        return session.get ( 'User_id' )

    def get_post(self, post_id):
        """
        Retrieves a post by its ID from the database.

        Args:
            post_id (int): The ID of the post.

        Returns:
            Post or None: The post object if found, otherwise None.
        """
        return Post.query.get ( post_id )

    def toggle_like(self, user_id, post):
        """
        Toggles the like status for the given post.

        If the user has already liked the post, it unlikes it.
        Otherwise, it likes the post.

        Args:
            user_id (int): The ID of the user.
            post (Post): The post object to like/unlike.

        Returns:
            (bool, str): Success status and a message if applicable.
        """
        # Check if the user has already liked the post
        like = Like.query.filter_by ( user_id=user_id, post_id=post.id ).first ()

        if like:
            # User has already liked the post, so "unlike" it
            db.session.delete ( like )
            # Ensure likes_count does not go below 0
            if post.likes_count > 0:
                post.likes_count -= 1  # Decrease like count
            return True, "Post unliked"
        else:
            # User hasn't liked the post, so "like" it
            new_like = Like ( user_id=user_id, post_id=post.id )
            db.session.add ( new_like )
            post.likes_count += 1  # Increase like count
            return True, "Post liked"

    def create_error_response(self, message, status_code):
        """
        Creates a JSON error response.

        Args:
            message (str): The error message to send.
            status_code (int): The HTTP status code to send.

        Returns:
            JSON response with error message and status code.
        """
        return jsonify ( {"success": False, "message": message} ), status_code


class Logout ( Resource ):
    """
    Handles user logout functionality.

    This resource removes the 'User_id' from the session and redirects the user
    to the login page, while also flashing a logout success message.
    """

    def post(self):
        """
        Logs the user out by clearing the 'User_id' from the session.

        After logging out, the user is redirected to the login page with a success
        flash message indicating that they have been logged out.

        Returns:
            Response: Redirect to the login page.
        """
        # Remove the user ID from the session to log out the user
        session.pop ( 'User_id', None )

        # Flash a success message
        flash ( 'You have been logged out.', 'success' )

        # Redirect to the login page
        return redirect ( url_for ( 'login' ) )


class CommentBox(Resource):
    def post(self):
        # Get the data from the form
        user_id = request.form.get('user_id')
        post_id = request.form.get('post_id')
        comment_text = request.form.get('comment_text')

        if not comment_text:
            return redirect(url_for('dashboard', post_id=post_id))  # Redirect back if comment is empty

        # Create a new comment instance
        new_comment = Comment(user_id=user_id, post_id=post_id, text=comment_text)

        # Add the comment to the database
        db.session.add(new_comment)
        db.session.commit()
        comments = Comment.query.filter_by ().all ()

        # Redirect back to the post page (this will display the newly added comment)
        return redirect(url_for('dashboard', post_id=post_id,comments=comments))