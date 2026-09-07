# [M] OpenStack Compute (Nova) Improper Access Control 

## Summary
Severity: Medium
Advisory: GHSA-97fv-22hc-mrgj
CVE: CVE-2015-2687
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-97fv-22hc-mrgj
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=0 <15.0.0.0b1

## Details
OpenStack Compute (nova) Icehouse, Juno and Havana when live migration fails allows local users to access VM volumes that they would normally not have permissions for.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-2687
- https://github.com/openstack/nova/commit/b83cae02ece4c338e09c3606c6ae69b715bd6f8c
- https://bugs.launchpad.net/nova/+bug/1419577
- https://bugzilla.redhat.com/show_bug.cgi?id=1205313
- https://github.com/openstack/nova
- https://github.com/pypa/advisory-database/tree/main/vulns/nova/PYSEC-2017-145.yaml
- https://review.openstack.org/#/c/338929
- http://www.openwall.com/lists/oss-security/2015/03/24/10
- http://www.openwall.com/lists/oss-security/2015/03/25/3
