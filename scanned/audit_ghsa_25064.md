# [H] OpenStack Swift Discloses Secret URLs to Timing Attack

## Summary
Severity: High
Advisory: GHSA-cf9m-q836-vf26
CVE: CVE-2014-0006
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-cf9m-q836-vf26
Type: github-advisory

## Affected
- PyPI: `swift` — affected >=1.4.6
- PyPI: `swift` — affected >=1.9.0
- PyPI: `swift` — affected >=1.11.0 <1.12.0

## Details
The TempURL middleware in OpenStack Object Storage (Swift) 1.4.6 through 1.8.0, 1.9.0 through 1.10.0, and 1.11.0 allows remote attackers to obtain secret URLs by leveraging an object name and a timing side-channel attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0006
- https://github.com/openstack/swift/commit/754633988931e4095530f6b13389c254096eb485
- https://bugs.launchpad.net/swift/+bug/1265665
- https://github.com/openstack/swift
- https://github.com/pypa/advisory-database/tree/main/vulns/swift/PYSEC-2014-116.yaml
- http://rhn.redhat.com/errata/RHSA-2014-0232.html
- http://www.openwall.com/lists/oss-security/2014/01/17/5
