# [M] OpenStack Keystone Improper Authentication vulnerability

## Summary
Severity: Medium
Advisory: GHSA-22q6-wwq7-2jj9
CVE: CVE-2013-1865
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-22q6-wwq7-2jj9
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=2012.2 <2012.2.4

## Details
OpenStack Keystone Folsom (2012.2) does not properly perform revocation checks for Keystone PKI tokens when done through a server, which allows remote attackers to bypass intended access restrictions via a revoked PKI token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1865
- https://access.redhat.com/errata/RHSA-2013:0708
- https://access.redhat.com/security/cve/CVE-2013-1865
- https://bugs.launchpad.net/keystone/+bug/1129713
- https://bugzilla.redhat.com/show_bug.cgi?id=922230
- https://github.com/pypa/advisory-database/tree/main/vulns/keystone/PYSEC-2013-39.yaml
- https://opendev.org/openstack/keystone
- https://review.openstack.org/#/c/24906
- https://review.openstack.org/24906
- https://web.archive.org/web/20170715155558/http://www.securityfocus.com/bid/58616
- http://github.com/openstack/keystone/commit/255b1d43500f5d98ec73a0056525b492b14fec05
- http://lists.fedoraproject.org/pipermail/package-announce/2013-April/101719.html
- http://lists.opensuse.org/opensuse-updates/2013-04/msg00000.html
- http://rhn.redhat.com/errata/RHSA-2013-0708.html
- http://www.openwall.com/lists/oss-security/2013/03/20/13
- http://www.ubuntu.com/usn/USN-1772-1
