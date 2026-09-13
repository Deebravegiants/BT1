# [H] OpenStack Swift Unchecked user input in XML responses

## Summary
Severity: High
Advisory: GHSA-9xgv-6v35-mmcj
CVE: CVE-2013-2161
CWE: CWE-94
Ecosystem: PyPI
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-9xgv-6v35-mmcj
Type: github-advisory

## Affected
- PyPI: `swift` — affected >=0 <1.9.0

## Details
XML injection vulnerability in account/utils.py in OpenStack Swift Folsom, Grizzly, and Havana allows attackers to trigger invalid or spoofed Swift responses via an account name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2161
- https://github.com/openstack/swift/commit/6659382c4fa348e1ebbce2424968dd7267ea1db1
- https://github.com/openstack/swift/commit/8f9b135e0a16478a628f20224ce5babe62d4aaba
- https://bugs.launchpad.net/swift/+bug/1183884
- https://github.com/openstack/swift
- http://github.com/openstack/swift/commit/4eed6bf5b5028409f730be97ddcfb6bfa893c976
- http://github.com/openstack/swift/commit/92d7eadd328797d392758c79e258c8455874c80e
- http://lists.opensuse.org/opensuse-updates/2013-07/msg00021.html
- http://rhn.redhat.com/errata/RHSA-2013-0993.html
- http://www.debian.org/security/2012/dsa-2737
- http://www.openwall.com/lists/oss-security/2013/06/13/4
