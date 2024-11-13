from flask_restful import Api
from resource import Register, Home, Login, Logout, Dashboard, ForgotPassword, ResetPassword, Add_Post, UpdateProfile, profile, LikePost,CommentBox

def add_routes(api: Api):
    api.add_resource(Register, '/register')  # Register user
    api.add_resource(Home, '/')  # Home page
    api.add_resource(Login, '/login')  # Login page
    api.add_resource(Logout, '/logout')  # Logout
    api.add_resource(Dashboard, '/dashboard', '/dashboard/<int:User_id>')  # User dashboard
    api.add_resource(ForgotPassword, '/forgot-password')  # Forgot password
    api.add_resource(ResetPassword, '/reset_password')  # Reset password
    api.add_resource(Add_Post, '/add_post', '/add_post/<int:Post_id>/delete')  # Add or delete posts
    api.add_resource(UpdateProfile, '/update_profile', '/update_profile/<int:Profile_id>')  # Update Profile
    api.add_resource( profile, '/profile', '/profile/<int:User_id>' )  # User Profile
    api.add_resource(LikePost, '/like/<int:post_id>')  # Like a post
    api.add_resource(CommentBox, '/comments', '/comments/<int:post_id>')