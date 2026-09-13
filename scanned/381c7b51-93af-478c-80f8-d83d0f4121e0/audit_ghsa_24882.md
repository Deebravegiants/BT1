# [M] OpenStack Object Storage (Swift) Sensitive Data Exposure

## Summary
Severity: Medium
Advisory: GHSA-q45h-chc8-hvp6
CVE: CVE-2015-5223
CWE: CWE-200
Ecosystem: PyPI
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-q45h-chc8-hvp6
Type: github-advisory

## Affected
- PyPI: `swift` — affected >=0 <2.4.0

## Details
OpenStack Object Storage (Swift) before 2.4.0 allows attackers to obtain sensitive information via a PUT tempurl and a DLO object manifest that references an object in another container.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5223
- https://bugs.launchpad.net/swift/+bug/1449212
- https://bugs.launchpad.net/swift/+bug/1453948
- https://github.com/openstack/swift
- https://security.openstack.org/ossa/OSSA-2015-016.html
- https://web.archive.org/web/20200804233308/http://www.securityfocus.com/bid/84827
- http://lists.opensuse.org/opensuse-security-announce/2015-10/msg00025.html
- http://rhn.redhat.com/errata/RHSA-2015-1895.html
- http://rhn.redhat.com/errata/RHSA-2016-0329.html
- http://www.openwall.com/lists/oss-security/2015/08/26/5
- http://www.oracle.com/technetwork/topics/security/bulletinapr2016-2952098.html
