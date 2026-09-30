# [M] OpenStack Swift metadata constraints are not correctly enforced

## Summary
Severity: Medium
Advisory: GHSA-g6x3-55qv-x6p2
CVE: CVE-2014-7960
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-g6x3-55qv-x6p2
Type: github-advisory

## Affected
- PyPI: `swift` — affected >=0 <2.2.0

## Details
OpenStack Object Storage (Swift) before 2.2.0 allows remote authenticated users to bypass the max_meta_count and other metadata constraints via multiple crafted requests which exceed the limit when combined.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-7960
- https://github.com/openstack/swift/commit/06800cbe446ce4c937a57b69517b55c3bba9b6e1
- https://github.com/openstack/swift/commit/2c4622a28ea04e1c6b2382189b0a1f6cccdc9c0f
- https://github.com/openstack/swift/commit/5b2c27a5874c2b5b0a333e4955b03544f6a8119f
- https://bugs.launchpad.net/swift/+bug/1365350
- https://exchange.xforce.ibmcloud.com/vulnerabilities/96901
- https://github.com/openstack/swift
- http://lists.opensuse.org/opensuse-security-announce/2015-10/msg00025.html
- http://rhn.redhat.com/errata/RHSA-2015-0835.html
- http://rhn.redhat.com/errata/RHSA-2015-0836.html
- http://rhn.redhat.com/errata/RHSA-2015-1495.html
- http://www.openwall.com/lists/oss-security/2014/10/07/39
- http://www.openwall.com/lists/oss-security/2014/10/08/7
- http://www.oracle.com/technetwork/topics/security/bulletinjan2015-2370101.html
- http://www.securityfocus.com/bid/70279
- http://www.ubuntu.com/usn/USN-2704-1
