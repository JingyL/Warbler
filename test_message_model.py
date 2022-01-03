"""Message View tests."""

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes
from models import db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()

class MessageModelTestCase(TestCase):
    """test"""
    def setUp(self):
        """Create sample."""
        db.drop_all()
        db.create_all()

        self.user_id = 999
        user = User.signup("testing", "testing@gmail.com", "1234", None)
        user.id = self.user_id
        db.session.commit()

        self.user = User.query.get(self.user_id)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        """Test message model"""
        
        message = Message(
            text="aaaa",
            user_id=self.user_id
        )

        db.session.add(message)
        db.session.commit()

        self.assertEqual(self.user.messages[0].text, "aaaa")

    def test_message_likes(self):
        m1 = Message(
            text="aaaa",
            user_id=self.user_id
        )

        m2 = Message(
            text="bbbbb",
            user_id=self.user_id 
        )

        new_user = User.signup("testing2", "testing2@gmail.com", "12345", None)
        user_id = 9999
        new_user.id = user_id
        db.session.add_all([m1, m2, new_user])
        db.session.commit()

        new_user.likes.append(m1)

        db.session.commit()

        l = Likes.query.filter(Likes.user_id == user_id).all()
        self.assertEqual(l[0].message_id, m1.id)    