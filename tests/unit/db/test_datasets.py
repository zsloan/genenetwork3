"""Tests for gn3/db/datasets.py"""

from unittest import mock, TestCase
from gn3.db.datasets import (
    retrieve_dataset_name,
    retrieve_riset_fields,
    retrieve_geno_riset_fields,
    retrieve_publish_riset_fields,
    retrieve_probeset_riset_fields)

class TestDatasetsDBFunctions(TestCase):
    """Test cases for datasets functions."""

    def test_retrieve_dataset_name(self):
        """Test that the function is called correctly."""
        for trait_type, thresh, trait_name, dataset_name, columns, table in [
                ["ProbeSet", 9, "probesetTraitName", "probesetDatasetName",
                 "Id, Name, FullName, ShortName, DataScale", "ProbeSetFreeze"],
                ["Geno", 3, "genoTraitName", "genoDatasetName",
                 "Id, Name, FullName, ShortName", "GenoFreeze"],
                ["Publish", 6, "publishTraitName", "publishDatasetName",
                 "Id, Name, FullName, ShortName", "PublishFreeze"],
                ["Temp", 4, "tempTraitName", "tempTraitName",
                 "Id, Name, FullName, ShortName", "TempFreeze"]]:
            db_mock = mock.MagicMock()
            with self.subTest(trait_type=trait_type):
                with db_mock.cursor() as cursor:
                    cursor.fetchone.return_value = {}
                    self.assertEqual(
                        retrieve_dataset_name(
                            trait_type, thresh, trait_name, dataset_name, db_mock),
                        {})
                    cursor.execute.assert_called_once_with(
                        "SELECT {cols} "
                        "FROM {table} "
                        "WHERE public > %(threshold)s AND "
                        "(Name = %(name)s "
                        "OR FullName = %(name)s "
                        "OR ShortName = %(name)s)".format(
                            table=table, cols=columns),
                        {"threshold": thresh, "name": dataset_name})

    def test_retrieve_probeset_riset_fields(self):
        """
        Test that the `riset` and `riset_id` fields are retrieved appropriately
        for the 'ProbeSet' trait type.
        """
        for trait_name, expected in [
                ["testProbeSetName", {}]]:
            db_mock = mock.MagicMock()
            with self.subTest(trait_name=trait_name, expected=expected):
                with db_mock.cursor() as cursor:
                    cursor.execute.return_value = ()
                    self.assertEqual(
                        retrieve_probeset_riset_fields(trait_name, db_mock),
                        expected)
                    cursor.execute.assert_called_once_with(
                        (
                            "SELECT InbredSet.Name, InbredSet.Id"
                            " FROM InbredSet, ProbeSetFreeze, ProbeFreeze"
                            " WHERE ProbeFreeze.InbredSetId = InbredSet.Id"
                            " AND ProbeFreeze.Id = ProbeSetFreeze.ProbeFreezeId"
                            " AND ProbeSetFreeze.Name = %(name)s"),
                        {"name": trait_name})

    def test_retrieve_riset_fields(self):
        """
        Test that the riset fields are set up correctly for the different trait
        types.
        """
        for trait_type, trait_name, dataset_info, expected in [
                ["Publish", "pubTraitName01", {"dataset_name": "pubDBName01"},
                 {"dataset_name": "pubDBName01", "riset": ""}],
                ["ProbeSet", "prbTraitName01", {"dataset_name": "prbDBName01"},
                 {"dataset_name": "prbDBName01", "riset": ""}],
                ["Geno", "genoTraitName01", {"dataset_name": "genoDBName01"},
                 {"dataset_name": "genoDBName01", "riset": ""}],
                ["Temp", "tempTraitName01", {}, {"riset": ""}],
                ]:
            db_mock = mock.MagicMock()
            with self.subTest(
                    trait_type=trait_type, trait_name=trait_name,
                    dataset_info=dataset_info):
                with db_mock.cursor() as cursor:
                    cursor.execute.return_value = ("riset_name", 0)
                    self.assertEqual(
                        retrieve_riset_fields(
                            trait_type, trait_name, dataset_info, db_mock),
                        expected)

    def test_retrieve_publish_riset_fields(self):
        """
        Test that the `riset` and `riset_id` fields are retrieved appropriately
        for the 'Publish' trait type.
        """
        for trait_name, expected in [
                ["testPublishName", {}]]:
            db_mock = mock.MagicMock()
            with self.subTest(trait_name=trait_name, expected=expected):
                with db_mock.cursor() as cursor:
                    cursor.execute.return_value = ()
                    self.assertEqual(
                        retrieve_publish_riset_fields(trait_name, db_mock),
                        expected)
                    cursor.execute.assert_called_once_with(
                        (
                            "SELECT InbredSet.Name, InbredSet.Id"
                            " FROM InbredSet, PublishFreeze"
                            " WHERE PublishFreeze.InbredSetId = InbredSet.Id"
                            " AND PublishFreeze.Name = %(name)s"),
                        {"name": trait_name})

    def test_retrieve_geno_riset_fields(self):
        """
        Test that the `riset` and `riset_id` fields are retrieved appropriately
        for the 'Geno' trait type.
        """
        for trait_name, expected in [
                ["testGenoName", {}]]:
            db_mock = mock.MagicMock()
            with self.subTest(trait_name=trait_name, expected=expected):
                with db_mock.cursor() as cursor:
                    cursor.execute.return_value = ()
                    self.assertEqual(
                        retrieve_geno_riset_fields(trait_name, db_mock),
                        expected)
                    cursor.execute.assert_called_once_with(
                        (
                            "SELECT InbredSet.Name, InbredSet.Id"
                            " FROM InbredSet, GenoFreeze"
                            " WHERE GenoFreeze.InbredSetId = InbredSet.Id"
                            " AND GenoFreeze.Name = %(name)s"),
                        {"name": trait_name})
