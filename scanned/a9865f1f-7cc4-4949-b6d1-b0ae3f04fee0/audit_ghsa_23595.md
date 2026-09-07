# [H] python-keystoneclient missing expiration check in PKI token validation 

## Summary
Severity: High
Advisory: GHSA-4rrr-j7ff-r844
CVE: CVE-2013-2104
CWE: CWE-324
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-4rrr-j7ff-r844
Type: github-advisory

## Affected
- PyPI: `python-keystoneclient` — affected >=0 <0.2.4

## Details
python-keystoneclient before 0.2.4, as used in OpenStack Keystone (Folsom), does not properly check expiry for PKI tokens, which allows remote authenticated users to (1) retain use of a token after it has expired, or (2) use a revoked token once it expires.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2104
- https://access.redhat.com/errata/RHSA-2013:0944
- https://access.redhat.com/security/cve/CVE-2013-2104
- https://bugs.launchpad.net/python-keystoneclient/+bug/1179615
- https://bugzilla.redhat.com/show_bug.cgi?id=965852
- https://github.com/openstack/python-keystoneclient
- https://github.com/pypa/advisory-database/tree/main/vulns/python-keystoneclient/PYSEC-2014-69.yaml
- http://lists.opensuse.org/opensuse-updates/2013-06/msg00198.html
- http://rhn.redhat.com/errata/RHSA-2013-0944.html
- http://www.openwall.com/lists/oss-security/2013/05/28/7
- http://www.ubuntu.com/usn/USN-1851-1
- http://www.ubuntu.com/usn/USN-1875-1
