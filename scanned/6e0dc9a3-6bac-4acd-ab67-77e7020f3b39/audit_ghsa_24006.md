# [M] OpenStack Swift allows authenticated users to cause a denial of service

## Summary
Severity: Medium
Advisory: GHSA-wxx2-gqvv-34hx
CVE: CVE-2013-4155
CWE: CWE-119
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-wxx2-gqvv-34hx
Type: github-advisory

## Affected
- PyPI: `swift` — affected >=0 <1.9.1

## Details
OpenStack Swift before 1.9.1 in Folsom, Grizzly, and Havana allows authenticated users to cause a denial of service ("superfluous" tombstone consumption and Swift cluster slowdown) via a DELETE request with a timestamp that is older than expected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4155
- https://github.com/openstack/swift/commit/1f4ec235cdfd8c868f2d6458532f9dc32c00b8ca
- https://github.com/openstack/swift/commit/6b9806e0e8cbec60c0a3ece0bd516e0502827515
- https://bugs.launchpad.net/swift/+bug/1196932
- https://github.com/openstack/swift
- https://review.openstack.org/#/c/40643
- https://review.openstack.org/#/c/40645
- https://review.openstack.org/#/c/40646
- http://rhn.redhat.com/errata/RHSA-2013-1197.html
- http://www.debian.org/security/2012/dsa-2737
- http://www.openwall.com/lists/oss-security/2013/08/07/6
- http://www.ubuntu.com/usn/USN-2001-1
