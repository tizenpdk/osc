import osc.core
import osc.oscerr
import os
from common import GET, OscTestCase
FIXTURES_DIR = os.path.join(os.getcwd(), 'tests/init_project_fixtures')

def suite():
    import unittest
    return unittest.makeSuite(TestInitProject)

class TestInitProject(OscTestCase):
    def _get_fixtures_dir(self):
        # workaround for git because it doesn't allow empty dirs
        if not os.path.exists(os.path.join(FIXTURES_DIR, 'osctest')):
            os.mkdir(os.path.join(FIXTURES_DIR, 'osctest'))
        return FIXTURES_DIR

    def tearDown(self):
        if os.path.exists(os.path.join(FIXTURES_DIR, 'osctest')):
            os.rmdir(os.path.join(FIXTURES_DIR, 'osctest'))
        OscTestCase.tearDown(self)

    def test_simple(self):
        """initialize a project dir"""
        prj_dir = os.path.join(self.tmpdir, 'testprj')
        prj = osc.core.Project.init_project('http://localhost', prj_dir, 'testprj', getPackageList=False)
        self.assertTrue(isinstance(prj, osc.core.Project))
        storedir = os.path.join(prj_dir, osc.core.store)
        self._check_list(os.path.join(storedir, '_project'), 'testprj\n')
        self._check_list(os.path.join(storedir, '_apiurl'), 'http://localhost\n')
        self._check_list(os.path.join(storedir, '_packages'), '<project name="testprj" />')

    def test_dirExists(self):
        """initialize a project dir but the dir already exists"""
        prj_dir = os.path.join(self.tmpdir, 'testprj')
        os.mkdir(prj_dir)
        prj = osc.core.Project.init_project('http://localhost', prj_dir, 'testprj', getPackageList=False)
        self.assertTrue(isinstance(prj, osc.core.Project))
        storedir = os.path.join(prj_dir, osc.core.store)
        self._check_list(os.path.join(storedir, '_project'), 'testprj\n')
        self._check_list(os.path.join(storedir, '_apiurl'), 'http://localhost\n')
        self._check_list(os.path.join(storedir, '_packages'), '<project name="testprj" />')

    def test_storedirExists(self):
        """initialize a project dir but the storedir already exists"""
        prj_dir = os.path.join(self.tmpdir, 'testprj')
        os.mkdir(prj_dir)
        os.mkdir(os.path.join(prj_dir, osc.core.store))
        self.assertRaises(osc.oscerr.OscIOError, osc.core.Project.init_project, 'http://localhost', prj_dir, 'testprj')

    @GET('http://localhost/source/testprj', text='<directory count="0" />')
    def test_no_package_tracking(self):
        """initialize a project dir but disable package tracking; enable getPackageList=True;
        disable wc_check (because we didn't disable the package tracking before the Project class
        was imported therefore REQ_STOREFILES contains '_packages')
        """
        import osc.conf
        # disable package tracking
        osc.conf.config['do_package_tracking'] = False
        prj_dir = os.path.join(self.tmpdir, 'testprj')
        os.mkdir(prj_dir)
        prj = osc.core.Project.init_project('http://localhost', prj_dir, 'testprj', False, wc_check=False)
        self.assertTrue(isinstance(prj, osc.core.Project))
        storedir = os.path.join(prj_dir, osc.core.store)
        self._check_list(os.path.join(storedir, '_project'), 'testprj\n')
        self._check_list(os.path.join(storedir, '_apiurl'), 'http://localhost\n')
        self.assertFalse(os.path.exists(os.path.join(storedir, '_packages')))

if __name__ == '__main__':
    import unittest
    unittest.main()
