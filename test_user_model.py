"""User model tests."""
import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()
        self.user1 = User(
            email="test1@gmail.com",
            username="test1",
            password="12345"
        )

        self.user2 = User(
            email="test2@gmail.com",
            username="test2",
            password="12345"
        )

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_user_model(self):
        """Does basic model work?"""

        user = User(
            email="test@gmail.com",
            username="test",
            password="12345"
        )
        db.session.add(user)
        db.session.commit()
        self.assertEqual(len(user.messages), 0)
        self.assertEqual(len(user.followers), 0)


    def test_user_follows(self):
        self.user1.following.append(self.user2)
        self.user2.followers.append(self.user1)
        db.session.commit()

        self.assertEqual(len(self.user2.following), 0)
        self.assertEqual(len(self.user2.followers), 1)
        self.assertEqual(len(self.user1.followers), 0)
        self.assertEqual(len(self.user1.following), 1)

        self.assertEqual(self.user2.followers[0].id, self.user1.id)
        self.assertEqual(self.user1.following[0].id, self.user2.id)

    def test_is_following(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user1.is_following(self.user2))
        self.assertFalse(self.user2.is_following(self.user1))

    def test_is_followed_by(self):
        self.user2.followers.append(self.user1)
        db.session.commit()

        self.assertTrue(self.user2.is_followed_by(self.user1))
        self.assertFalse(self.user1.is_followed_by(self.user2))

    def test_valid_signup(self):
        user = User.signup("test3", "test3@gmail.com", "12345", None)
        user_id = 9999999
        user.id = user_id
        db.session.commit()

        test_user = User.query.get(user_id)
        self.assertEqual(test_user.username, "test3")
        self.assertEqual(test_user.email, "test3@gmail.com")
        self.assertNotEqual(test_user.password, "12345")

    def test_invalid_username_signup(self):
        invalid = User.signup(None, "test@test.com", "12345", None)
        uid = 123456789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        invalid = User.signup("testtest", None, "12345", None)
        uid = 123789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", "", None)
        
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", None, None)

    def test_valid_authentication(self):
        user1 = User.authenticate(self.user1.username, self.user1.password)
        self.assertIsNotNone(user1)
    
    def test_invalid_username(self):
        self.assertFalse(User.authenticate("badusername", "12345"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.user1.username, "1234"))
