# [M] Openstack tripleo-heat-templates unauthenticated file access

## Summary
Severity: Medium
Advisory: GHSA-w8gx-hhcx-px6w
CVE: CVE-2017-12155
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-w8gx-hhcx-px6w
Type: github-advisory

## Affected
- PyPI: `tripleo-heat-templates` — affected >=0 <7.0.6

## Details
A resource-permission flaw was found in the `tripleo-heat-templates` package where `ceph.client.openstack.keyring` is created as world-readable. A local attacker with access to the key could read or modify data on Ceph cluster pools for OpenStack as though the attacker were the OpenStack service, thus potentially reading or modifying data in an OpenStack Block Storage volume. This has been patched in versions [7.0.6](https://github.com/openstack/tripleo-heat-templates/commit/a18fd59077d97de83496c85c017b9d256a3eddd4) and [8.0.0](https://github.com/openstack/tripleo-heat-templates/commit/ce7b65f443d38a6627631f53cb22336338e97d30).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12155
- https://access.redhat.com/errata/RHSA-2018:0602
- https://access.redhat.com/errata/RHSA-2018:1593
- https://access.redhat.com/errata/RHSA-2018:1627
- https://bugs.launchpad.net/tripleo/+bug/1720787
- https://bugzilla.redhat.com/show_bug.cgi?id=1489360
- https://github.com/openstack/tripleo-heat-templates
- https://opendev.org/openstack/tripleo-heat-templates/commit/a18fd59077d97de83496c85c017b9d256a3eddd4
- https://opendev.org/openstack/tripleo-heat-templates/commit/ce7b65f443d38a6627631f53cb22336338e97d30
