# [H] OpenStack Object Storage (Swift) allows remote attackers to cause a denial of service

## Summary
Severity: High
Advisory: GHSA-fxwr-2vxm-cg7p
CVE: CVE-2016-0738
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-fxwr-2vxm-cg7p
Type: github-advisory

## Affected
- PyPI: `swift` — affected >=0 <2.3.1
- PyPI: `swift` — affected >=2.4.0 <2.5.1

## Details
OpenStack Object Storage (Swift) before 2.3.1 (Kilo), 2.4.x, and 2.5.x before 2.5.1 (Liberty) do not properly close server connections, which allows remote attackers to cause a denial of service (proxy-server resource consumption) via a series of interrupted requests to a Large Object URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-0738
- https://web.archive.org/web/20200228001102/http://www.securityfocus.com/bid/81432
- https://security.openstack.org/ossa/OSSA-2016-004.html
- https://rhn.redhat.com/errata/RHSA-2016-0329.html
- https://rhn.redhat.com/errata/RHSA-2016-0155.html
- https://rhn.redhat.com/errata/RHSA-2016-0128.html
- https://lists.fedoraproject.org/pipermail/package-announce/2016-February/176713.html
- https://github.com/openstack/swift/blob/master/CHANGELOG
- https://github.com/openstack/swift
- https://bugzilla.redhat.com/show_bug.cgi?id=1298905
- https://bugs.launchpad.net/cloud-archive/+bug/1493303
- https://access.redhat.com/security/cve/CVE-2016-0738
- https://access.redhat.com/errata/RHSA-2016:0329
- https://access.redhat.com/errata/RHSA-2016:0328
- https://access.redhat.com/errata/RHSA-2016:0155
- https://access.redhat.com/errata/RHSA-2016:0128
- https://access.redhat.com/errata/RHSA-2016:0127
- https://access.redhat.com/errata/RHSA-2016:0126
