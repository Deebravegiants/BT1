# [C] OpenStack Object Storage (swift) Code Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-v7mh-3jgf-r26c
CVE: CVE-2012-4406
CWE: CWE-502, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-v7mh-3jgf-r26c
Type: github-advisory

## Affected
- PyPI: `swift` — affected >=0 <1.7.0

## Details
OpenStack Object Storage (swift) before 1.7.0 uses the loads function in the pickle Python module unsafely when storing and loading metadata in memcached, which allows remote attackers to execute arbitrary code via a crafted pickle object.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-4406
- https://github.com/openstack/swift/commit/e1ff51c04554d51616d2845f92ab726cb0e5831a
- https://access.redhat.com/errata/RHSA-2012:1379
- https://access.redhat.com/errata/RHSA-2013:0691
- https://access.redhat.com/security/cve/CVE-2012-4406
- https://bugs.launchpad.net/swift/+bug/1006414
- https://bugzilla.redhat.com/show_bug.cgi?id=854757
- https://exchange.xforce.ibmcloud.com/vulnerabilities/79140
- https://launchpad.net/swift/+milestone/1.7.0
- https://opendev.org/openstack/swift
- https://web.archive.org/web/20130629092623/http://www.securityfocus.com/bid/55420
- http://lists.fedoraproject.org/pipermail/package-announce/2012-October/089472.html
- http://rhn.redhat.com/errata/RHSA-2012-1379.html
- http://rhn.redhat.com/errata/RHSA-2013-0691.html
- http://www.openwall.com/lists/oss-security/2012/09/05/16
- http://www.openwall.com/lists/oss-security/2012/09/05/4
- http://www.securityfocus.com/bid/55420
