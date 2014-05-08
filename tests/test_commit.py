import osc.core
import osc.oscerr
import os
import sys
from common import GET, PUT, POST, DELETE, OscTestCase
from xml.etree import cElementTree as ET
FIXTURES_DIR = os.path.join(os.getcwd(), 'commit_fixtures')

def suite():
    import unittest
    return unittest.makeSuite(TestCommit)

rev_dummy = '<revision rev="repository">\n  <srcmd5>empty</srcmd5>\n</revision>'

class TestCommit(OscTestCase):
    def _get_fixtures_dir(self):
        return FIXTURES_DIR

    @GET('http://localhost/source/osctest/simple?rev=latest', file='testSimple_filesremote')
    @POST('http://localhost/source/osctest/simple?cmd=getprojectservices',
          exp='', text='<services />')
    @POST('http://localhost/source/osctest/simple?comment=&cmd=commitfilelist&user=Admin',
          file='testSimple_missingfilelist', expfile='testSimple_lfilelist')
    @PUT('http://localhost/source/osctest/simple/nochange?rev=repository',
          exp='This file didn\'t change but\nis modified.\n', text=rev_dummy)
    @POST('http://localhost/source/osctest/simple?comment=&cmd=commitfilelist&user=Admin',
          file='testSimple_cfilesremote', expfile='testSimple_lfilelist')
    def test_simple(self):
        """a simple commit (only one modified file)"""
        self._change_to_pkg('simple')
        p = osc.core.Package('.')
        p.commit()
        exp = 'Sending    nochange\nTransmitting file data .\nCommitted revision 2.\n'
        self.assertEqual(sys.stdout.getvalue(), exp)
        self._check_digests('testSimple_cfilesremote')
        self.assertTrue(os.path.exists('nochange'))
        self.assertEqual(open('nochange', 'r').read(), open(os.path.join('.osc', 'nochange'), 'r').read())
        self._check_status(p, 'nochange', ' ')
        self._check_status(p, 'foo', ' ')
        self._check_status(p, 'merge', ' ')

    @GET('http://localhost/source/osctest/add?rev=latest', file='testAddfile_filesremote')
    @POST('http://localhost/source/osctest/add?cmd=getprojectservices',
          exp='', text='<services />')
    @POST('http://localhost/source/osctest/add?comment=&cmd=commitfilelist&user=Admin',
          file='testAddfile_missingfilelist', expfile='testAddfile_lfilelist')
    @PUT('http://localhost/source/osctest/add/add?rev=repository',
         exp='added file\n', text=rev_dummy)
    @POST('http://localhost/source/osctest/add?comment=&cmd=commitfilelist&user=Admin',
          file='testAddfile_cfilesremote', expfile='testAddfile_lfilelist')
    def test_addfile(self):
        """commit a new file"""
        self._change_to_pkg('add')
        p = osc.core.Package('.')
        p.commit()
        exp = 'Sending    add\nTransmitting file data .\nCommitted revision 2.\n'
        self.assertEqual(sys.stdout.getvalue(), exp)
        self._check_digests('testAddfile_cfilesremote')
        self.assertTrue(os.path.exists('add'))
        self.assertEqual(open('add', 'r').read(), open(os.path.join('.osc', 'add'), 'r').read())
        self.assertFalse(os.path.exists(os.path.join('.osc', '_to_be_added')))
        self._check_status(p, 'add', ' ')
        self._check_status(p, 'foo', ' ')
        self._check_status(p, 'merge', ' ')
        self._check_status(p, 'nochange', ' ')

    @GET('http://localhost/source/osctest/delete?rev=latest', file='testDeletefile_filesremote')
    @POST('http://localhost/source/osctest/delete?cmd=getprojectservices',
          exp='', text='<services />')
    @POST('http://localhost/source/osctest/delete?comment=&cmd=commitfilelist&user=Admin',
          file='testDeletefile_cfilesremote', expfile='testDeletefile_lfilelist')
    def test_deletefile(self):
        """delete a file"""
        self._change_to_pkg('delete')
        p = osc.core.Package('.')
        p.commit()
        exp = 'Deleting    nochange\nTransmitting file data \nCommitted revision 2.\n'
        self.assertEqual(sys.stdout.getvalue(), exp)
        self._check_digests('testDeletefile_cfilesremote')
        self.assertFalse(os.path.exists('nochange'))
        self.assertFalse(os.path.exists(os.path.join('.osc', 'nochange')))
        self.assertFalse(os.path.exists(os.path.join('.osc', '_to_be_deleted')))
        self._check_status(p, 'foo', ' ')
        self._check_status(p, 'merge', ' ')

    @GET('http://localhost/source/osctest/conflict?rev=latest', file='testConflictfile_filesremote')
    @POST('http://localhost/source/osctest/conflict?cmd=getprojectservices',
          exp='', text='<services />')
    def test_conflictfile(self):
        """package has a file which is in conflict state"""
        self._change_to_pkg('conflict')
        ret = osc.core.Package('.').commit()
        self.assertTrue(ret == 1)
        exp = 'Please resolve all conflicts before committing using "osc resolved FILE"!\n'
        self.assertEqual(sys.stdout.getvalue(), exp)
        self._check_digests('testConflictfile_filesremote')
        self._check_conflictlist('merge\n')

    @GET('http://localhost/source/osctest/nochanges?rev=latest', file='testNoChanges_filesremote')
    @POST('http://localhost/source/osctest/nochanges?cmd=getprojectservices',
          exp='', text='<services />')
    def test_nochanges(self):
        """package has no changes (which can be committed)"""
        self._change_to_pkg('nochanges')
        p = osc.core.Package('.')
        ret = p.commit()
        self.assertTrue(ret == 1)
        exp = 'nothing to do for package nochanges\n'
        self.assertEqual(sys.stdout.getvalue(), exp)
        self._check_status(p, 'foo', 'S')
        self._check_status(p, 'merge', '!')
        self._check_status(p, 'nochange', ' ')

    @GET('http://localhost/source/osctest/multiple?rev=latest', file='testMultiple_filesremote')
    @POST('http://localhost/source/osctest/multiple?cmd=getprojectservices',
          exp='', text='<services />')
    @POST('http://localhost/source/osctest/multiple?comment=&cmd=commitfilelist&user=Admin',
          file='testMultiple_missingfilelist', expfile='testMultiple_lfilelist')
    @PUT('http://localhost/source/osctest/multiple/nochange?rev=repository', exp='This file did change.\n', text=rev_dummy)
    @PUT('http://localhost/source/osctest/multiple/add?rev=repository', exp='added file\n', text=rev_dummy)
    @PUT('http://localhost/source/osctest/multiple/add2?rev=repository', exp='add2\n', text=rev_dummy)
    @POST('http://localhost/source/osctest/multiple?comment=&cmd=commitfilelist&user=Admin',
          file='testMultiple_cfilesremote', expfile='testMultiple_lfilelist')
    def test_multiple(self):
        """a simple commit (only one modified file)"""
        self._change_to_pkg('multiple')
        p = osc.core.Package('.')
        p.commit()
        exp = 'Deleting    foo\nDeleting    merge\nSending    nochange\n' \
            'Sending    add\nSending    add2\nTransmitting file data ...\nCommitted revision 2.\n'
        self.assertEqual(sys.stdout.getvalue(), exp)
        self._check_digests('testMultiple_cfilesremote')
        self.assertFalse(os.path.exists(os.path.join('.osc', '_to_be_added')))
        self.assertFalse(os.path.exists(os.path.join('.osc', '_to_be_deleted')))
        self.assertFalse(os.path.exists(os.path.join('.osc', 'foo')))
        self.assertFalse(os.path.exists(os.path.join('.osc', 'merge')))
        self.assertRaises(osc.oscerr.OscIOError, p.status, 'foo')
        self.assertRaises(osc.oscerr.OscIOError, p.status, 'merge')
        self._check_status(p, 'add', ' ')
        self._check_status(p, 'add2', ' ')
        self._check_status(p, 'nochange', ' ')

    @GET('http://localhost/source/osctest/multiple?rev=latest', file='testPartial_filesremote')
    @POST('http://localhost/source/osctest/multiple?cmd=getprojectservices',
          exp='', text='<services />')
    @POST('http://localhost/source/osctest/multiple?comment=&cmd=commitfilelist&user=Admin',
          file='testPartial_missingfilelist', expfile='testPartial_lfilelist')
    @PUT('http://localhost/source/osctest/multiple/add?rev=repository', exp='added file\n', text=rev_dummy)
    @PUT('http://localhost/source/osctest/multiple/nochange?rev=repository', exp='This file did change.\n', text=rev_dummy)
    @POST('http://localhost/source/osctest/multiple?comment=&cmd=commitfilelist&user=Admin',
          file='testPartial_cfilesremote', expfile='testPartial_lfilelist')
    def test_partial(self):
        """commit only some files"""
        self._change_to_pkg('multiple')
        p = osc.core.Package('.')
        p.todo = ['foo', 'add', 'nochange']
        p.commit()
        exp = 'Deleting    foo\nSending    nochange\n' \
            'Sending    add\nTransmitting file data ..\nCommitted revision 2.\n'
        self.assertEqual(sys.stdout.getvalue(), exp)
        self._check_digests('testPartial_cfilesremote')
        self._check_addlist('add2\n')
        self._check_deletelist('merge\n')
        self._check_status(p, 'add2', 'A')
        self._check_status(p, 'merge', 'D')
        self._check_status(p, 'add', ' ')
        self._check_status(p, 'nochange', ' ')
        self.assertRaises(osc.oscerr.OscIOError, p.status, 'foo')

    @GET('http://localhost/source/osctest/simple?rev=latest', file='testSimple_filesremote')
    @POST('http://localhost/source/osctest/simple?cmd=getprojectservices',
          exp='', text='<services />')
    @POST('http://localhost/source/osctest/simple?comment=&cmd=commitfilelist&user=Admin',
          file='testSimple_missingfilelist', expfile='testSimple_lfilelist')
    @PUT('http://localhost/source/osctest/simple/nochange?rev=repository', exp='This file didn\'t change but\nis modified.\n',
        exception=IOError('test exception'), text=rev_dummy)
    def test_interrupt(self):
        """interrupt a commit"""
        self._change_to_pkg('simple')
        p = osc.core.Package('.')
        self.assertRaises(IOError, p.commit)
        exp = 'Sending    nochange\nTransmitting file data .'
        self.assertTrue(sys.stdout.getvalue(), exp)
        self._check_digests('testSimple_filesremote')
        self.assertTrue(os.path.exists('nochange'))
        self._check_status(p, 'nochange', 'M')

    @GET('http://localhost/source/osctest/allstates?rev=latest', file='testPartial_filesremote')
    @POST('http://localhost/source/osctest/allstates?cmd=getprojectservices',
          exp='', text='<services />')
    @POST('http://localhost/source/osctest/allstates?comment=&cmd=commitfilelist&user=Admin',
          file='testAllStates_missingfilelist', expfile='testAllStates_lfilelist')
    @PUT('http://localhost/source/osctest/allstates/add?rev=repository', exp='added file\n', text=rev_dummy)
    @PUT('http://localhost/source/osctest/allstates/missing?rev=repository', exp='replaced\n', text=rev_dummy)
    @PUT('http://localhost/source/osctest/allstates/nochange?rev=repository', exp='This file did change.\n', text=rev_dummy)
    @POST('http://localhost/source/osctest/allstates?comment=&cmd=commitfilelist&user=Admin',
          file='testAllStates_cfilesremote', expfile='testAllStates_lfilelist')
    def test_allstates(self):
        """commit all files (all states are available except 'C')"""
        self._change_to_pkg('allstates')
        p = osc.core.Package('.')
        p.commit()
        exp = 'Deleting    foo\nSending    missing\nSending    nochange\n' \
            'Sending    add\nTransmitting file data ...\nCommitted revision 2.\n'
        self.assertEqual(sys.stdout.getvalue(), exp)
        self._check_digests('testAllStates_expfiles', 'skipped')
        self.assertFalse(os.path.exists(os.path.join('.osc', '_to_be_added')))
        self.assertFalse(os.path.exists(os.path.join('.osc', '_to_be_deleted')))
        self.assertFalse(os.path.exists('foo'))
        self.assertFalse(os.path.exists(os.path.join('.osc', 'foo')))
        self._check_status(p, 'add', ' ')
        self._check_status(p, 'nochange', ' ')
        self._check_status(p, 'merge', '!')
        self._check_status(p, 'missing', ' ')
        self._check_status(p, 'skipped', 'S')
        self._check_status(p, 'test', ' ')

    @GET('http://localhost/source/osctest/add?rev=latest', file='testAddfile_filesremote')
    @POST('http://localhost/source/osctest/add?cmd=getprojectservices',
          exp='', text='<services />')
    @POST('http://localhost/source/osctest/add?comment=&cmd=commitfilelist&user=Admin',
          file='testAddfile_cfilesremote', expfile='testAddfile_lfilelist')
    def test_remoteexists(self):
        """file 'add' should be committed but already exists on the server"""
        self._change_to_pkg('add')
        p = osc.core.Package('.')
        p.commit()
        exp = 'Sending    add\nTransmitting file data \nCommitted revision 2.\n'
        self.assertEqual(sys.stdout.getvalue(), exp)
        self._check_digests('testAddfile_cfilesremote')
        self.assertTrue(os.path.exists('add'))
        self.assertEqual(open('add', 'r').read(), open(os.path.join('.osc', 'add'), 'r').read())
        self.assertFalse(os.path.exists(os.path.join('.osc', '_to_be_added')))
        self._check_status(p, 'add', ' ')
        self._check_status(p, 'foo', ' ')
        self._check_status(p, 'merge', ' ')
        self._check_status(p, 'nochange', ' ')

    @GET('http://localhost/source/osctest/branch?rev=latest', file='testExpand_filesremote')
    @POST('http://localhost/source/osctest/branch?cmd=getprojectservices',
          exp='', text='<services />')
    @POST('http://localhost/source/osctest/branch?comment=&cmd=commitfilelist&user=Admin&keeplink=1',
          file='testExpand_missingfilelist', expfile='testExpand_lfilelist')
    @PUT('http://localhost/source/osctest/branch/simple?rev=repository', exp='simple modified file.\n', text=rev_dummy)
    @POST('http://localhost/source/osctest/branch?comment=&cmd=commitfilelist&user=Admin&keeplink=1',
          file='testExpand_cfilesremote', expfile='testExpand_lfilelist')
    @GET('http://localhost/source/osctest/branch?rev=87ea02aede261b0267aabaa97c756e7a', file='testExpand_expandedfilesremote')
    def test_expand(self):
        """commit an expanded package"""
        self._change_to_pkg('branch')
        p = osc.core.Package('.')
        p.commit()
        exp = 'Sending    simple\nTransmitting file data .\nCommitted revision 7.\n'
        self.assertEqual(sys.stdout.getvalue(), exp)
        self._check_digests('testExpand_expandedfilesremote')
        self._check_status(p, 'simple', ' ')

    @GET('http://localhost/source/osctest/added_missing?rev=latest', file='testAddedMissing_filesremote')
    @POST('http://localhost/source/osctest/added_missing?cmd=getprojectservices',
          exp='', text='<services />')
    def test_added_missing(self):
        """commit an added file which is missing"""
        self._change_to_pkg('added_missing')
        p = osc.core.Package('.')
        ret = p.commit()
        self.assertTrue(ret == 1)
        exp = 'file \'add\' is marked as \'A\' but does not exist\n'
        self.assertEqual(sys.stdout.getvalue(), exp)
        self._check_status(p, 'add', '!')

    @GET('http://localhost/source/osctest/added_missing?rev=latest', file='testAddedMissing_filesremote')
    @POST('http://localhost/source/osctest/added_missing?cmd=getprojectservices',
          exp='', text='<services />')
    @POST('http://localhost/source/osctest/added_missing?comment=&cmd=commitfilelist&user=Admin',
          file='testAddedMissing_missingfilelist', expfile='testAddedMissing_lfilelist')
    @PUT('http://localhost/source/osctest/added_missing/bar?rev=repository', exp='foobar\n', text=rev_dummy)
    @POST('http://localhost/source/osctest/added_missing?comment=&cmd=commitfilelist&user=Admin',
          file='testAddedMissing_cfilesremote', expfile='testAddedMissing_lfilelist')
    def test_added_missing2(self):
        """commit an added file, another added file missing (but it's not part of the commit)"""
        self._change_to_pkg('added_missing')
        p = osc.core.Package('.')
        p.todo = ['bar']
        p.commit()
        exp = 'Sending    bar\nTransmitting file data .\nCommitted revision 2.\n'
        self.assertEqual(sys.stdout.getvalue(), exp)
        self._check_status(p, 'add', '!')
        self._check_status(p, 'bar', ' ')

if __name__ == '__main__':
    import unittest
    unittest.main()
