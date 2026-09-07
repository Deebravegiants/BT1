# [M] OpenStack Swift Unauthorized delete of versioned Swift object

## Summary
Severity: Medium
Advisory: GHSA-cc77-5vw4-7pwg
CVE: CVE-2015-1856
Ecosystem: PyPI
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-cc77-5vw4-7pwg
Type: github-advisory

## Affected
- PyPI: `swift` — affected >=0 <2.3.0

## Details
OpenStack Object Storage (Swift) before 2.3.0, when allow_version is configured, allows remote authenticated users to delete the latest version of an object by leveraging listing access to the x-versions-location container.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-1856
- https://bugs.launchpad.net/swift/+bug/1430645
- https://git.openstack.org/cgit/openstack/swift/commit/?id=5bb7c286ebb4a54e4d2bd5a02845644d1c651183
- https://git.openstack.org/cgit/openstack/swift/commit/?id=85afe9316570855c87ea731d0627f6f8f2b73264
- https://git.openstack.org/cgit/openstack/swift/commit/?id=dd9d97458ea007024220a78dba8dd663e8b425d7
- https://git.openstack.org/cgit/openstack/swift/commit/?id=f6525758ab2456d688430699338993439597a789
- https://github.com/openstack/swift
- http://lists.fedoraproject.org/pipermail/package-announce/2015-August/163113.html
- http://lists.openstack.org/pipermail/openstack-announce/2015-April/000349.html
- http://lists.opensuse.org/opensuse-security-announce/2015-10/msg00025.html
- http://rhn.redhat.com/errata/RHSA-2015-1681.html
- http://rhn.redhat.com/errata/RHSA-2015-1684.html
- http://rhn.redhat.com/errata/RHSA-2015-1845.html
- http://rhn.redhat.com/errata/RHSA-2015-1846.html
- http://www.oracle.com/technetwork/topics/security/bulletinapr2015-2511959.html
- http://www.securityfocus.com/bid/74182
- http://www.ubuntu.com/usn/USN-2704-1
