# -*- coding: utf-8 -*-
import fauxfactory
import pytest
from random import sample

import cfme.utils
from cfme.utils.blockers import BZ
from cfme.utils.providers import get_crud_by_name
from cfme import test_requirements


@pytest.fixture(scope="function")
def report_vms(appliance, infra_provider):
    report = appliance.collections.reports.create(
        menu_name=fauxfactory.gen_alphanumeric(),
        title=fauxfactory.gen_alphanumeric(),
        base_report_on="Virtual Machines",
        report_fields=[
            "Provider : Name",
            "Cluster / Deployment Role : Name",
            "Datastore : Name",
            "Hardware : Number of CPUs",
            "Hardware : RAM",
            "Host / Node : Name",
            "Name",
        ]
    )
    report.queue(wait_for_finish=True)
    yield sample(
        filter(
            lambda i: len(i["Provider Name"].strip()) > 0,
            list(report.saved_reports.all()[0].data.rows)), 2)
    report.delete()


@pytest.mark.tier(3)
@pytest.mark.rhv3
@pytest.mark.meta(blockers=[BZ(1531600, forced_streams=['5.9'])])
@test_requirements.report
def test_custom_vm_report(soft_assert, report_vms):
    cluster = "Cluster / Deployment Role Name"
    host = "Host / Node Name"
    for row in report_vms:
        if row["Name"].startswith("test_"):
            continue  # Might disappear meanwhile
        provider_name = row["Provider Name"]
        provider_mgmt = get_crud_by_name(provider_name).mgmt
        provider_hosts_and_ips = cfme.utils.net.resolve_ips(provider_mgmt.list_host())
        provider_datastores = provider_mgmt.list_datastore()
        provider_clusters = provider_mgmt.list_cluster()
        soft_assert(provider_mgmt.does_vm_exist(row["Name"]),
                    "VM {} does not exist in {}!".format(row["Name"], provider_name))
        if row[cluster]:
            soft_assert(
                row[cluster] in provider_clusters,
                "Cluster {} not found in {}!".format(row[cluster], str(provider_clusters))
            )
        if row["Datastore Name"]:
            soft_assert(
                row["Datastore Name"] in provider_datastores,
                "Datastore {} not found in {}!".format(
                    row["Datastore Name"], str(provider_datastores))
            )
        # Because of mixing long and short host names, we have to use both-directional `in` op.
        if row[host]:
            found = False
            possible_ips_or_hosts = cfme.utils.net.resolve_ips((row[host], ))
            for possible_ip_or_host in possible_ips_or_hosts:
                for host_ip in provider_hosts_and_ips:
                    if possible_ip_or_host in host_ip or host_ip in possible_ip_or_host:
                        found = True
            soft_assert(
                found,
                "Host {} not found in {}!".format(possible_ips_or_hosts, provider_hosts_and_ips)
            )
