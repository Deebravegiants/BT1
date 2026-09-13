# [H] OpenStack Identity service (keystone) Incorrect Authorization

## Summary
Severity: High
Advisory: GHSA-j36m-hv43-7w7m
CVE: CVE-2017-2673
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-j36m-hv43-7w7m
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=9.0.0
- PyPI: `keystone` — affected >=10.0.0 <10.0.2
- PyPI: `keystone` — affected >=11.0.0 <11.0.1

## Details
An authorization-check flaw was discovered in federation configurations of the OpenStack Identity service (keystone). An authenticated federated user could request permissions to a project and unintentionally be granted all related roles including administrative roles.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-2673
- https://github.com/openstack/keystone/commit/05a129e54573b6cbda1ec095f4526f2b9ba90a90
- https://github.com/openstack/keystone/commit/2139639eeabc8f6941f4461fc87d609cde3118c2
- https://access.redhat.com/errata/RHSA-2017:1461
- https://access.redhat.com/errata/RHSA-2017:1597
- https://access.redhat.com/security/cve/CVE-2017-2673
- https://bugs.launchpad.net/keystone/+bug/1677723
- https://bugzilla.redhat.com/show_bug.cgi?id=1439586
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2673
- https://github.com/openstack/keystone
- https://github.com/pypa/advisory-database/tree/main/vulns/keystone/PYSEC-2018-152.yaml
- http://seclists.org/oss-sec/2017/q2/125
- http://www.securityfocus.com/bid/98032
