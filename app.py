from __init__ import create_app
from model import db

# Create the Flask app using the factory function
app = create_app()

if __name__ == "__main__":
    with app.app_context ():
        # db.drop_all()
        db.create_all ()
    app.run ( debug=False )

