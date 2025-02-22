"""Tests for gn3/db/traits.py"""
from unittest import mock, TestCase
from gn3.db.traits import (
    build_trait_name,
    set_haveinfo_field,
    update_sample_data,
    retrieve_trait_info,
    set_confidential_field,
    set_homologene_id_field,
    retrieve_geno_trait_info,
    retrieve_temp_trait_info,
    retrieve_publish_trait_info,
    retrieve_probeset_trait_info)

class TestTraitsDBFunctions(TestCase):
    "Test cases for traits functions"

    def test_retrieve_publish_trait_info(self):
        """Test retrieval of type `Publish` traits."""
        db_mock = mock.MagicMock()
        with db_mock.cursor() as cursor:
            cursor.fetchone.return_value = tuple()
            trait_source = {
                "trait_name": "PublishTraitName", "trait_dataset_id": 1}
            self.assertEqual(
                retrieve_publish_trait_info(trait_source, db_mock), {})
            cursor.execute.assert_called_once_with(
                ("SELECT "
                 "PublishXRef.Id, Publication.PubMed_ID,"
                 " Phenotype.Pre_publication_description,"
                 " Phenotype.Post_publication_description,"
                 " Phenotype.Original_description,"
                 " Phenotype.Pre_publication_abbreviation,"
                 " Phenotype.Post_publication_abbreviation,"
                 " Phenotype.Lab_code, Phenotype.Submitter, Phenotype.Owner,"
                 " Phenotype.Authorized_Users,"
                 " CAST(Publication.Authors AS BINARY),"
                 " Publication.Title, Publication.Abstract,"
                 " Publication.Journal,"
                 " Publication.Volume, Publication.Pages, Publication.Month,"
                 " Publication.Year, PublishXRef.Sequence, Phenotype.Units,"
                 " PublishXRef.comments"
                 " FROM"
                 " PublishXRef, Publication, Phenotype, PublishFreeze"
                 " WHERE"
                 " PublishXRef.Id = %(trait_name)s"
                 " AND Phenotype.Id = PublishXRef.PhenotypeId"
                 " AND Publication.Id = PublishXRef.PublicationId"
                 " AND PublishXRef.InbredSetId = PublishFreeze.InbredSetId"
                 " AND PublishFreeze.Id =%(trait_dataset_id)s"),
                trait_source)

    def test_retrieve_probeset_trait_info(self):
        """Test retrieval of type `Probeset` traits."""
        db_mock = mock.MagicMock()
        with db_mock.cursor() as cursor:
            cursor.fetchone.return_value = tuple()
            trait_source = {
                "trait_name": "ProbeSetTraitName",
                "trait_dataset_name": "ProbeSetDatasetTraitName"}
            self.assertEqual(
                retrieve_probeset_trait_info(trait_source, db_mock), {})
            cursor.execute.assert_called_once_with(
                (
                    "SELECT "
                    "ProbeSet.name, ProbeSet.symbol, ProbeSet.description, "
                    "ProbeSet.probe_target_description, ProbeSet.chr, "
                    "ProbeSet.mb, ProbeSet.alias, ProbeSet.geneid, "
                    "ProbeSet.genbankid, ProbeSet.unigeneid, ProbeSet.omim, "
                    "ProbeSet.refseq_transcriptid, ProbeSet.blatseq, "
                    "ProbeSet.targetseq, ProbeSet.chipid, ProbeSet.comments, "
                    "ProbeSet.strand_probe, ProbeSet.strand_gene, "
                    "ProbeSet.probe_set_target_region, ProbeSet.proteinid, "
                    "ProbeSet.probe_set_specificity, "
                    "ProbeSet.probe_set_blat_score, "
                    "ProbeSet.probe_set_blat_mb_start, "
                    "ProbeSet.probe_set_blat_mb_end, "
                    "ProbeSet.probe_set_strand, ProbeSet.probe_set_note_by_rw, "
                    "ProbeSet.flag "
                    "FROM "
                    "ProbeSet, ProbeSetFreeze, ProbeSetXRef "
                    "WHERE "
                    "ProbeSetXRef.ProbeSetFreezeId = ProbeSetFreeze.Id "
                    "AND ProbeSetXRef.ProbeSetId = ProbeSet.Id "
                    "AND ProbeSetFreeze.Name = %(trait_dataset_name)s "
                    "AND ProbeSet.Name = %(trait_name)s"), trait_source)

    def test_retrieve_geno_trait_info(self):
        """Test retrieval of type `Geno` traits."""
        db_mock = mock.MagicMock()
        with db_mock.cursor() as cursor:
            cursor.fetchone.return_value = tuple()
            trait_source = {
                "trait_name": "GenoTraitName",
                "trait_dataset_name": "GenoDatasetTraitName"}
            self.assertEqual(
                retrieve_geno_trait_info(trait_source, db_mock), {})
            cursor.execute.assert_called_once_with(
                (
                    "SELECT "
                    "Geno.name, Geno.chr, Geno.mb, Geno.source2, Geno.sequence "
                    "FROM "
                    "Geno, GenoFreeze, GenoXRef "
                    "WHERE "
                    "GenoXRef.GenoFreezeId = GenoFreeze.Id "
                    "AND GenoXRef.GenoId = Geno.Id "
                    "AND GenoFreeze.Name = %(trait_dataset_name)s "
                    "AND Geno.Name = %(trait_name)s"),
                trait_source)

    def test_retrieve_temp_trait_info(self):
        """Test retrieval of type `Temp` traits."""
        db_mock = mock.MagicMock()
        with db_mock.cursor() as cursor:
            cursor.fetchone.return_value = tuple()
            trait_source = {"trait_name": "TempTraitName"}
            self.assertEqual(
                retrieve_temp_trait_info(trait_source, db_mock), {})
            cursor.execute.assert_called_once_with(
                "SELECT name, description FROM Temp WHERE Name = %(trait_name)s",
                trait_source)

    def test_build_trait_name_with_good_fullnames(self):
        """
        Check that the name is built correctly.
        """
        for fullname, expected in [
                ["testdb::testname",
                 {"db": {"dataset_name": "testdb", "dataset_type": "ProbeSet"},
                  "trait_name": "testname", "cellid": "",
                  "trait_fullname": "testdb::testname"}],
                ["testdb::testname::testcell",
                 {"db": {"dataset_name": "testdb", "dataset_type": "ProbeSet"},
                  "trait_name": "testname", "cellid": "testcell",
                  "trait_fullname": "testdb::testname::testcell"}]]:
            with self.subTest(fullname=fullname):
                self.assertEqual(build_trait_name(fullname), expected)

    def test_build_trait_name_with_bad_fullnames(self):
        """
        Check that an exception is raised if the full name format is wrong.
        """
        for fullname in ["", "test", "test:test"]:
            with self.subTest(fullname=fullname):
                with self.assertRaises(AssertionError, msg="Name format error"):
                    build_trait_name(fullname)

    def test_retrieve_trait_info(self):
        """Test that information on traits is retrieved as appropriate."""
        for threshold, trait_fullname, expected in [
                [9, "pubDb::PublishTraitName::pubCell", {"haveinfo": 0}],
                [5, "prbDb::ProbeSetTraitName::prbCell", {"haveinfo": 0}],
                [12, "genDb::GenoTraitName", {"haveinfo": 0}],
                [6, "tmpDb::TempTraitName", {"haveinfo": 0}]]:
            db_mock = mock.MagicMock()
            with self.subTest(trait_fullname=trait_fullname):
                with db_mock.cursor() as cursor:
                    cursor.fetchone.return_value = tuple()
                    self.assertEqual(
                        retrieve_trait_info(
                            threshold, trait_fullname, db_mock),
                        expected)

    def test_update_sample_data(self):
        """Test that the SQL queries when calling update_sample_data are called with
        the right calls.

        """
        db_mock = mock.MagicMock()

        STRAIN_ID_SQL: str = "UPDATE Strain SET Name = %s WHERE Id = %s"
        PUBLISH_DATA_SQL: str = ("UPDATE PublishData SET value = %s "
                                 "WHERE StrainId = %s AND Id = %s")
        PUBLISH_SE_SQL: str = ("UPDATE PublishSE SET error = %s "
                               "WHERE StrainId = %s AND DataId = %s")
        N_STRAIN_SQL: str = ("UPDATE NStrain SET count = %s "
                             "WHERE StrainId = %s AND DataId = %s")

        with db_mock.cursor() as cursor:
            type(cursor).rowcount = 1
            self.assertEqual(update_sample_data(
                conn=db_mock, strain_name="BXD11",
                strain_id=10, publish_data_id=8967049,
                value=18.7, error=2.3, count=2),
                             (1, 1, 1, 1))
            cursor.execute.assert_has_calls(
                [mock.call(STRAIN_ID_SQL, ('BXD11', 10)),
                 mock.call(PUBLISH_DATA_SQL, (18.7, 10, 8967049)),
                 mock.call(PUBLISH_SE_SQL, (2.3, 10, 8967049)),
                 mock.call(N_STRAIN_SQL, (2, 10, 8967049))]
            )

    def test_set_haveinfo_field(self):
        """Test that the `haveinfo` field is set up correctly"""
        for trait_info, expected in [
                [{}, {"haveinfo": 0}],
                [{"k1": "v1"}, {"k1": "v1", "haveinfo": 1}]]:
            with self.subTest(trait_info=trait_info, expected=expected):
                self.assertEqual(set_haveinfo_field(trait_info), expected)

    def test_set_homologene_id_field(self):
        """Test that the `homologene_id` field is set up correctly"""
        for trait_type, trait_info, expected in [
                ["Publish", {}, {"homologeneid": None}],
                ["ProbeSet", {}, {"homologeneid": None}],
                ["Geno", {}, {"homologeneid": None}],
                ["Temp", {}, {"homologeneid": None}]]:
            db_mock = mock.MagicMock()
            with self.subTest(trait_info=trait_info, expected=expected):
                with db_mock.cursor() as cursor:
                    cursor.fetchone.return_value = ()
                    self.assertEqual(
                        set_homologene_id_field(trait_type, trait_info, db_mock), expected)

    def test_set_confidential_field(self):
        """Test that the `confidential` field is set up correctly"""
        for trait_type, trait_info, expected in [
                ["Publish", {}, {"confidential": 0}],
                ["ProbeSet", {}, {}],
                ["Geno", {}, {}],
                ["Temp", {}, {}]]:
            with self.subTest(trait_info=trait_info, expected=expected):
                self.assertEqual(
                    set_confidential_field(trait_type, trait_info), expected)
