import os
import app as flaskr
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.testing = True
        self.app = flaskr.app.test_client()
        with flaskr.app.app_context():
            flaskr.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'No entries here so far' in rv.data

    # testing add post
    def test_messages(self):
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here',
            category='A category'
        ), follow_redirects=True)

        assert b'Unbelievable. No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data
        assert b'A category' in rv.data

    # testing deleted post
    def test_messages2(self):
        rv = self.app.post('/delete_entry', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here',
            category='A category'
        ), follow_redirects=True)

        assert b'&lt;Hello&gt;' not in rv.data
        assert b'<strong>HTML</strong> allowed here' not in rv.data
        assert b'A category' not in rv.data

    #testing if title is changed
    def test_edit1(self):
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here',
            category='A category'
        ), follow_redirects=True)
        assert b'Unbelievable. No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data
        assert b'A category' in rv.data
        rv = self.app.post('/update_edited_entry', data=dict(
            updated_title='<Hello World>',
            updated_text='<strong>HTML</strong> allowed here',
            updated_category='A category',
            id = 1
        ), follow_redirects=True)
        assert b'Unbelievable. No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' not in rv.data
        assert b'&lt;Hello World&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data
        assert b'A category' in rv.data


# testing if text is edited
    def test_edit2(self):
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML!</strong> allowed here',
            category='A category'
        ), follow_redirects=True)
        assert b'Unbelievable. No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'&lt;strong&gt;HTML!&lt;strong&gt; allowed here' not in rv.data
        assert b'A category' in rv.data
        rv = self.app.post('/update_edited_entry', data=dict(
            updated_title='<Hello World>',
            updated_text='<strong>HTML</strong> allowed here',
            updated_category='A category',
            id=1
        ), follow_redirects=True)
        assert b'&lt;Hello&gt;' not in rv.data
        assert b'<strong>HTML</strong> allowed here'  in rv.data
        assert b'<strong>HTML!</strong> allowed here' not in rv.data
        assert b'A category' in rv.data


# Testing if items all items are edited
    def test_editall(self):
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML!</strong> allowed here',
            category='A category'

        ), follow_redirects=True)
        assert b'Unbelievable. No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'<strong>HTML!</strong> allowed here' in rv.data
        assert b'A category' in rv.data
        rv = self.app.post('/update_edited_entry', data=dict(
            updated_title='<Hello!>',
            updated_text='<strong>HTML!</strong> allowed here',
            updated_category='A category!',
            id=1

        ), follow_redirects=True)
        assert b'Unbelievable. No entries here so far' not in rv.data
        assert b'&lt;Hello!&gt;' in rv.data
        assert b'<strong>HTML!</strong> allowed here' in rv.data
        assert b'A category!' in rv.data

        # Testing if items stay the same if not edited
        def test_nonedit(self):
            rv = self.app.post('/add', data=dict(
                title='<Hello>',
                text='<strong>HTML!</strong> allowed here',
                category='A category'

            ), follow_redirects=True)
            assert b'Unbelievable. No entries here so far' not in rv.data
            assert b'&lt;Hello&gt;' in rv.data
            assert b'<strong>HTML!</strong> allowed here' in rv.data
            assert b'A category' in rv.data
            rv = self.app.post('/update_edited_entry', data=dict(
                updated_title='<Hello>',
                updated_text='<strong>HTML</strong> allowed here',
                updated_category='A category',
                id=1

            ), follow_redirects=True)
            assert b'Unbelievable. No entries here so far' not in rv.data
            assert b'&lt;Hello&gt;' in rv.data
            assert b'<strong>HTML</strong> allowed here' in rv.data
            assert b'A category' in rv.data


if __name__ == '__main__':
    unittest.main()