# [M] CVE-2018-18506

## Summary
Severity: Medium
Advisory: CVE-2018-18506
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-02-05
Source: https://osv.dev/vulnerability/CVE-2018-18506
Type: osv

## Details
When proxy auto-detection is enabled, if a web server serves a Proxy Auto-Configuration (PAC) file or if a PAC file is loaded locally, this PAC file can specify that requests to the localhost are to be sent through the proxy to another server. This behavior is disallowed by default when a proxy is manually configured, but when enabled could allow for attacks on services and tools that bind to the localhost for networked behavior if they are accessed through browsing. This vulnerability affects Firefox < 65.

## References
- https://usn.ubuntu.com/3927-1/
- https://www.debian.org/security/2019/dsa-4411
- http://lists.opensuse.org/opensuse-security-announce/2019-03/msg00043.html
- https://seclists.org/bugtraq/2019/Mar/28
- https://www.mozilla.org/security/advisories/mfsa2019-01/
- http://lists.opensuse.org/opensuse-security-announce/2019-03/msg00035.html
- https://access.redhat.com/errata/RHSA-2019:0622
- https://access.redhat.com/errata/RHSA-2019:0966
- https://seclists.org/bugtraq/2019/Apr/0
- https://www.debian.org/security/2019/dsa-4420
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00023.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00043.html
- http://www.securityfocus.com/bid/106773
- https://access.redhat.com/errata/RHSA-2019:0623
- https://access.redhat.com/errata/RHSA-2019:0680
- https://access.redhat.com/errata/RHSA-2019:0681
- https://access.redhat.com/errata/RHSA-2019:1144
- https://lists.debian.org/debian-lts-announce/2019/03/msg00024.html
- https://lists.debian.org/debian-lts-announce/2019/04/msg00000.html
- https://security.gentoo.org/glsa/201904-07
