# -*- coding: utf-8 -*-
import unittest
import os  # noqa: F401
import json  # noqa: F401
import time
import requests
import shutil
import gzip

from os import environ
try:
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3

from pprint import pprint  # noqa: F401

from Workspace.WorkspaceClient import Workspace as workspaceService
from SetAPI.SetAPIServiceClient import SetAPI
from ReadsUtils.ReadsUtilsClient import ReadsUtils

from kb_kaiju.kb_kaijuImpl import kb_kaiju
from kb_kaiju.kb_kaijuServer import MethodContext
from kb_kaiju.authclient import KBaseAuth as _KBaseAuth

from kb_kaiju.Utils.KaijuUtil import KaijuUtil
from kb_kaiju.Utils.DataStagingUtils import DataStagingUtils
from kb_kaiju.Utils.OutputBuilder import OutputBuilder


class kb_kaijuTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('kb_kaiju'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'kb_kaiju',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL)
        cls.serviceImpl = kb_kaiju(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']

        suffix = int(time.time() * 1000)
        cls.wsName = "test_kb_kaiju_" + str(suffix)
        cls.ws_info = cls.wsClient.create_workspace({'workspace': cls.wsName})

        cls.kaiju_runner = KaijuUtil(cls.cfg, cls.ctx)
        cls.ru = ReadsUtils(os.environ['SDK_CALLBACK_URL'])
        cls.setAPI = SetAPI(url=cls.cfg['srv-wiz-url'], token=cls.ctx['token'])

        # prepare WS data
        cls.prepare_data()


    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_kb_kaiju_" + str(suffix)
        ret = self.getWsClient().create_workspace({'workspace': wsName})  # noqa
        self.__class__.wsName = wsName
        return wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx


    @classmethod
    def prepare_data(cls):
        test_directory_name = 'test_kb_kaiju'
        cls.test_directory_path = os.path.join(cls.scratch, test_directory_name)
        os.makedirs(cls.test_directory_path)

        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = range(11)  # object_info tuple

        # upload Paired End Libs
        #
        cls.PE_reads_refs = []
        for basename in ['seven_species_nonuniform_10K-PE_reads_', 'seven_species_nonuniform_05K-PE_reads_']:
            fwd_filename = basename+'fwd-0.fastq'
            rev_filename = basename+'rev-0.fastq'
            reads_objname = basename+'.PElib'

            # put where ReadsUtils can see them (only sees shared scratch and requires unzipped)
            fwd_fastq_file_path = os.path.join(cls.scratch, fwd_filename)
            rev_fastq_file_path = os.path.join(cls.scratch, rev_filename)
            #shutil.copy(os.path.join("data", fwd_filename), fwd_fastq_file_path)
            #shutil.copy(os.path.join("data", rev_filename), rev_fastq_file_path)

            with gzip.open(os.path.join("data", fwd_filename+'.gz'), 'rb') as f_in, open(fwd_fastq_file_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
            with gzip.open(os.path.join("data", rev_filename+'.gz'), 'rb') as f_in, open(rev_fastq_file_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

            read_upload_params = {'fwd_file': fwd_fastq_file_path,
                                  'rev_file': rev_fastq_file_path,
                                  'sequencing_tech': 'artificial reads',
                                  'interleaved': 0,
                                  'wsname': cls.ws_info[1],
                                  'name': reads_objname
                              }
            reads_ref = cls.ru.upload_reads(read_upload_params)['obj_ref']
            cls.PE_reads_refs.append(reads_ref)
            pprint('Saved PE Lib Reads: ' + reads_ref)


        # Upload Single End Libraries
        #
        cls.SE_reads_refs = []
        for basename in ['seven_species_nonuniform_10K-PE_reads_', 'seven_species_nonuniform_05K-PE_reads_', 'SE_weird_readIDs_']:
            fwd_filename = basename+'fwd-0.fastq'
            #rev_filename = basename+'rev-0.fastq'
            reads_objname = basename+'.SElib'

            # put where ReadsUtils can see them (only sees shared scratch and requires unzipped)
            fwd_fastq_file_path = os.path.join(cls.scratch, fwd_filename)
            #rev_fastq_file_path = os.path.join(cls.scratch, rev_filename)
            #shutil.copy(os.path.join("data", fwd_filename), fwd_fastq_file_path)
            ##shutil.copy(os.path.join("data", rev_filename), rev_fastq_file_path)

            # already done above?
            if not os.path.isfile(fwd_fastq_file_path):
                #raise ValueError("no such file '"+fwd_fastq_file_path+"'")
                fwd_infile = os.path.join("data", fwd_filename)
                if os.path.isfile(fwd_infile+'.gz') and os.path.getsize(fwd_infile+'.gz') > 0:
                    with gzip.open(fwd_infile+'.gz', 'rb') as f_in, open(fwd_fastq_file_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                elif os.path.isfile(fwd_infile) and os.path.getsize(fwd_infile) > 0:
                    with open(fwd_infile, 'rb') as f_in, open(fwd_fastq_file_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                else:
                    raise ValueError("missing input file "+fwd_filename)

            if not os.path.isfile(fwd_fastq_file_path):
                raise ValueError("missing file '"+fwd_fastq_file_path+"'")
            elif not os.path.getsize(fwd_fastq_file_path) > 0:
                raise ValueError("empty file '"+fwd_fastq_file_path+"'")

            read_upload_params = {'fwd_file': fwd_fastq_file_path,
                                  #'rev_file': rev_fastq_file_path,
                                  'sequencing_tech': 'artificial reads',
                                  #'interleaved': 0,
                                  'wsname': cls.ws_info[1],
                                  'name': reads_objname
                              }
            reads_ref = cls.ru.upload_reads(read_upload_params)['obj_ref']
            cls.SE_reads_refs.append(reads_ref)
            pprint('Saved SE Lib Reads: ' + reads_ref)

            
    def _print_test_name (self, test_name):
        print ("\n"+('='*(10+len(test_name))))
        print ("RUNNING "+test_name+"()")
        print (('='*(10+len(test_name)))+"\n")
        return


    def _run_test_3_for_db (self, db_type):
        # run kaiju
        #input_refs = [self.PE_reads_refs[0]]
        input_refs = [self.PE_reads_refs[0], self.PE_reads_refs[1]]
        #output_biom_name = 'test_kb_kaiju_test1.BIOM'
        params = {
            'workspace_name':            self.ws_info[1],
            'input_refs':                input_refs,
            #'output_biom_name':          output_biom_name,
            'tax_levels':                ['phylum','genus'],
            #'tax_levels':                ['phylum'],
            'db_type':                   db_type,
            #'filter_percent':            1,
            'filter_percent':            0.5,
            #'subsample_percent':         100,
            'subsample_percent':         10,
            #'subsample_replicates':      1,
            'subsample_replicates':      1,
            'subsample_seed':            1,
            'seg_filter':                1,
            'min_match_length':          11,
            'greedy_run_mode':           1,
            'greedy_allowed_mismatches': 5,
            'greedy_min_match_score':    75,
            'greedy_max_e_value':        0.05,
            'filter_unclassified':       1,
            'full_tax_path':             0,
            'sort_taxa_by':              'totals'
        }
        result = self.getImpl().run_kaiju(self.getContext(), params)[0]

        pprint('End to end test result:')
        pprint(result)

        self.assertIn('report_name', result)
        self.assertIn('report_ref', result)

        # make sure the report was created and includes the HTML report and download links
        #rep = self.getWsClient().get_objects2({'objects': [{'ref': result['report_ref']}]})['data'][0]['data']
        #self.assertEquals(rep['direct_html_link_index'], 0)
        #self.assertEquals(len(rep['file_links']), 2)
        #self.assertEquals(len(rep['html_links']), 1)
        #self.assertEquals(rep['html_links'][0]['name'], 'report.html')

        return True
    
            
    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa


    ### Test 1: PE lib objects
    #
    # Uncomment to skip this test
    # HIDE @unittest.skip("skipped test_1_kaiju_PE_lib")
    def test_1_kaiju_PE_lib(self):
        self._print_test_name("test_1_kaiju_PE_lib")

        # run kaiju
        #input_refs = [self.PE_reads_refs[0]]
        input_refs = [self.PE_reads_refs[0], self.PE_reads_refs[1]]
        #output_biom_name = 'test_kb_kaiju_test1.BIOM'
        params = {
            'workspace_name':            self.ws_info[1],
            'input_refs':                input_refs,
            #'output_biom_name':          output_biom_name,
            'tax_levels':                ['phylum','genus'],
            #'tax_levels':                ['phylum'],
            'db_type':                   'refseq',
            #'filter_percent':            1,
            'filter_percent':            0.5,
            #'subsample_percent':         100,
            'subsample_percent':         10,
            #'subsample_replicates':      1,
            'subsample_replicates':      2,
            'subsample_seed':            1,
            'seg_filter':                1,
            'min_match_length':          11,
            'greedy_run_mode':           1,
            'greedy_allowed_mismatches': 5,
            'greedy_min_match_score':    75,
            'greedy_max_e_value':        0.05,
            'filter_unclassified':       1,
            'full_tax_path':             0,
            'sort_taxa_by':              'totals'
        }
        result = self.getImpl().run_kaiju(self.getContext(), params)[0]

        pprint('End to end test result:')
        pprint(result)

        self.assertIn('report_name', result)
        self.assertIn('report_ref', result)

        # make sure the report was created and includes the HTML report and download links
        #rep = self.getWsClient().get_objects2({'objects': [{'ref': result['report_ref']}]})['data'][0]['data']
        #self.assertEquals(rep['direct_html_link_index'], 0)
        #self.assertEquals(len(rep['file_links']), 2)
        #self.assertEquals(len(rep['html_links']), 1)
        #self.assertEquals(rep['html_links'][0]['name'], 'report.html')
        pass


    ### Test 1b: PE lib objects - mem mode
    #
    # Uncomment to skip this test
    # HIDE @unittest.skip("skipped test_1b_kaiju_PE_lib")
    def test_1b_kaiju_PE_lib_mem_mode(self):
        self._print_test_name('test_1b_kaiju_PE_lib_mem_mode')

        # run kaiju
        #input_refs = [self.PE_reads_refs[0]]
        input_refs = [self.PE_reads_refs[0], self.PE_reads_refs[1]]
        #output_biom_name = 'test_kb_kaiju_test1.BIOM'
        params = {
            'workspace_name':            self.ws_info[1],
            'input_refs':                input_refs,
            #'output_biom_name':          output_biom_name,
            'tax_levels':                ['phylum','genus'],
            #'tax_levels':                ['phylum'],
            'db_type':                   'refseq',
            #'filter_percent':            1,
            'filter_percent':            0.5,
            #'subsample_percent':         100,
            'subsample_percent':         10,
            #'subsample_replicates':      1,
            'subsample_replicates':      2,
            'subsample_seed':            1,
            'seg_filter':                1,
            'min_match_length':          11,
            'greedy_run_mode':           0,
            'greedy_allowed_mismatches': 5,
            'greedy_min_match_score':    75,
            'greedy_max_e_value':        0.05,
            'filter_unclassified':       1,
            'full_tax_path':             0,
            'sort_taxa_by':              'totals'
        }
        result = self.getImpl().run_kaiju(self.getContext(), params)[0]

        pprint('End to end test result:')
        pprint(result)

        self.assertIn('report_name', result)
        self.assertIn('report_ref', result)

        # make sure the report was created and includes the HTML report and download links
        #rep = self.getWsClient().get_objects2({'objects': [{'ref': result['report_ref']}]})['data'][0]['data']
        #self.assertEquals(rep['direct_html_link_index'], 0)
        #self.assertEquals(len(rep['file_links']), 2)
        #self.assertEquals(len(rep['html_links']), 1)
        #self.assertEquals(rep['html_links'][0]['name'], 'report.html')
        pass


    ### Test 2: SE lib object
    #
    # Uncomment to skip this test
    # HIDE @unittest.skip("skipped test_2_kaiju_SE_lib")
    def test_2_kaiju_SE_lib(self):
        self._print_test_name('test_2_kaiju_SE_lib')

        # run kaiju
        #input_refs = [self.SE_reads_refs[0]]
        input_refs = [self.SE_reads_refs[0], self.SE_reads_refs[1]]
        #output_biom_name = 'test_kb_kaiju_test2.BIOM'
        params = {
            'workspace_name':            self.ws_info[1],
            'input_refs':                input_refs,
            #'output_biom_name':          output_biom_name,
            'tax_levels':                ['phylum','genus'],
            #'tax_levels':                ['phylum'],
            'db_type':                   'refseq',
            #'filter_percent':            1,
            'filter_percent':            0.5,
            #'subsample_percent':         100,
            'subsample_percent':         10,
            #'subsample_replicates':      1,
            'subsample_replicates':      2,
            'subsample_seed':            1,
            'seg_filter':                1,
            'min_match_length':          11,
            'greedy_run_mode':           1,
            'greedy_allowed_mismatches': 5,
            'greedy_min_match_score':    75,
            'greedy_max_e_value':        0.05,
            'filter_unclassified':       1,
            'full_tax_path':             0,
            'sort_taxa_by':              'totals'
        }
        result = self.getImpl().run_kaiju(self.getContext(), params)[0]

        pprint('End to end test result:')
        pprint(result)

        self.assertIn('report_name', result)
        self.assertIn('report_ref', result)

        # make sure the report was created and includes the HTML report and download links
        #rep = self.getWsClient().get_objects2({'objects': [{'ref': result['report_ref']}]})['data'][0]['data']
        #self.assertEquals(rep['direct_html_link_index'], 0)
        #self.assertEquals(len(rep['file_links']), 2)
        #self.assertEquals(len(rep['html_links']), 1)
        #self.assertEquals(rep['html_links'][0]['name'], 'report.html')
        pass


    ### Test 2b: SE lib object - mem mode
    #
    # Uncomment to skip this test
    # HIDE @unittest.skip("skipped test_2b_kaiju_SE_lib_mem_mode")
    def test_2b_kaiju_SE_lib_mem_mode(self):
        self._print_test_name('test_2b_kaiju_SE_lib_mem_mode')

        # run kaiju
        #input_refs = [self.SE_reads_refs[0]]
        input_refs = [self.SE_reads_refs[0], self.SE_reads_refs[1]]
        #output_biom_name = 'test_kb_kaiju_test2.BIOM'
        params = {
            'workspace_name':            self.ws_info[1],
            'input_refs':                input_refs,
            #'output_biom_name':          output_biom_name,
            'tax_levels':                ['phylum','genus'],
            #'tax_levels':                ['phylum'],
            'db_type':                   'refseq',
            #'filter_percent':            1,
            'filter_percent':            0.5,
            #'subsample_percent':         100,
            'subsample_percent':         10,
            #'subsample_replicates':      1,
            'subsample_replicates':      2,
            'subsample_seed':            1,
            'seg_filter':                1,
            'min_match_length':          11,
            'greedy_run_mode':           0,
            'greedy_allowed_mismatches': 5,
            'greedy_min_match_score':    75,
            'greedy_max_e_value':        0.05,
            'filter_unclassified':       1,
            'full_tax_path':             0,
            'sort_taxa_by':              'totals'
        }
        result = self.getImpl().run_kaiju(self.getContext(), params)[0]

        pprint('End to end test result:')
        pprint(result)

        self.assertIn('report_name', result)
        self.assertIn('report_ref', result)

        # make sure the report was created and includes the HTML report and download links
        #rep = self.getWsClient().get_objects2({'objects': [{'ref': result['report_ref']}]})['data'][0]['data']
        #self.assertEquals(rep['direct_html_link_index'], 0)
        #self.assertEquals(len(rep['file_links']), 2)
        #self.assertEquals(len(rep['html_links']), 1)
        #self.assertEquals(rep['html_links'][0]['name'], 'report.html')
        pass


    #
    # Refseq already tested above
    #

    ### Test 3a: PE lib objects with NR
    #
    # Uncomment to skip this test
    @unittest.skip("skipped test_3a_kaiju_PE_lib_NR")
    def test_3a_kaiju_PE_lib_NR(self):
        self._print_test_name('test_3a_kaiju_PE_lib_NR')
        self._run_test_3_for_db ('nr')  # FAILING (too big for memory?)
        pass

    ### Test 3b: PE lib objects with NR_EUK
    #
    # Uncomment to skip this test
    @unittest.skip("skipped test_3b_kaiju_PE_lib_NR_EUK")
    def test_3b_kaiju_PE_lib_NR_EUK(self):
        self._print_test_name('test_3b_kaiju_PE_lib_NR_EUK')
        self._run_test_3_for_db ('nr_euk')  # FAILING (too big for memory?)
        pass

    ### Test 3c: PE lib objects with PROGENOMES
    #
    # Uncomment to skip this test
    # HIDE @unittest.skip("skipped test_3c_kaiju_PE_lib_PROGENOMES")
    def test_3c_kaiju_PE_lib_PROGENOMES(self):
        self._print_test_name('test_3c_kaiju_PE_lib_PROGENOMES')
        self._run_test_3_for_db ('progenomes')
        pass

    ### Test 3d: PE lib objects with PLASMIDS
    #
    # Uncomment to skip this test
    # HIDE @unittest.skip("skipped test_3d_kaiju_PE_lib_PLASMIDS")
    def test_3d_kaiju_PE_lib_PLASMIDS(self):
        self._print_test_name('test_3d_kaiju_PE_lib_PLASMIDS')
        self._run_test_3_for_db ('plasmids')
        pass

    ### Test 3e: PE lib objects with RVDB
    #
    # Uncomment to skip this test
    @unittest.skip("skipped test_3e_kaiju_PE_lib_aRVDB")
    def test_3e_kaiju_PE_lib_RVDB(self):
        self._print_test_name('test_3e_kaiju_PE_lib_RVDB')
        self._run_test_3_for_db ('rvdb')   # needs correct test query data
        pass

    ### Test 3f: PE lib objects with VIRUSES
    #
    # Uncomment to skip this test
    # HIDE @unittest.skip("skipped test_3f_kaiju_PE_lib_VIRUSES")
    def test_3f_kaiju_PE_lib_VIRUSES(self):
        self._print_test_name('test_3f_kaiju_PE_lib_VIRUSES')
        self._run_test_3_for_db ('viruses')
        pass

    ### Test 3g: PE lib objects with FUNGI
    #
    # Uncomment to skip this test
    # HIDE @unittest.skip("skipped test_3g_kaiju_PE_lib_FUNGI")
    def test_3g_kaiju_PE_lib_FUNGI(self):
        self._print_test_name('test_3g_kaiju_PE_lib_FUNGI')
        self._run_test_3_for_db ('fungi')
        pass
    
    
    ### Test 4: SE lib object with weird readIDs
    #
    # Uncomment to skip this test
    # HIDE @unittest.skip("skipped test_4_kaiju_SE_lib_weird_readIDs")
    def test_4_kaiju_SE_lib_weird_readIDs(self):
        self._print_test_name('test_4_kaiju_SE_lib_weird_readIDs')

        # run kaiju
        #input_refs = [self.SE_reads_refs[0]]
        input_refs = [self.SE_reads_refs[2]]
        #output_biom_name = 'test_kb_kaiju_test2.BIOM'
        params = {
            'workspace_name':            self.ws_info[1],
            'input_refs':                input_refs,
            #'output_biom_name':          output_biom_name,
            'tax_levels':                ['phylum','genus'],
            #'tax_levels':                ['phylum'],
            'db_type':                   'refseq',
            #'filter_percent':            1,
            'filter_percent':            0.5,
            #'subsample_percent':         100,
            'subsample_percent':         40,
            #'subsample_replicates':      1,
            'subsample_replicates':      1,
            'subsample_seed':            1,
            'seg_filter':                1,
            'min_match_length':          11,
            'greedy_run_mode':           1,
            'greedy_allowed_mismatches': 5,
            'greedy_min_match_score':    75,
            'greedy_max_e_value':        0.05,
            'filter_unclassified':       1,
            'full_tax_path':             0,
            'sort_taxa_by':              'totals'
        }
        result = self.getImpl().run_kaiju(self.getContext(), params)[0]

        pprint('End to end test result:')
        pprint(result)

        self.assertIn('report_name', result)
        self.assertIn('report_ref', result)

        # make sure the report was created and includes the HTML report and download links
        #rep = self.getWsClient().get_objects2({'objects': [{'ref': result['report_ref']}]})['data'][0]['data']
        #self.assertEquals(rep['direct_html_link_index'], 0)
        #self.assertEquals(len(rep['file_links']), 2)
        #self.assertEquals(len(rep['html_links']), 1)
        #self.assertEquals(rep['html_links'][0]['name'], 'report.html')
        pass

