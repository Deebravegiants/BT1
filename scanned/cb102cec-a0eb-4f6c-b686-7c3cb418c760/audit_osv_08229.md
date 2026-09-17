# [H] CVE-2016-1669

## Summary
Severity: High
Advisory: CVE-2016-1669
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-05-14
Source: https://osv.dev/vulnerability/CVE-2016-1669
Type: osv

## Details
The Zone::New function in zone.cc in Google V8 before 5.0.71.47, as used in Google Chrome before 50.0.2661.102, does not properly determine when to expand certain memory allocations, which allows remote attackers to cause a denial of service (buffer overflow) or possibly have unspecified other impact via crafted JavaScript code.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00043.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00050.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00048.html
- http://lists.opensuse.org/opensuse-updates/2016-07/msg00063.html
- http://www.securityfocus.com/bid/90584
- http://www.securitytracker.com/id/1035872
- https://codereview.chromium.org/1945313002
- https://crbug.com/606115
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05347541
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CITS5GIUTNWVSUXMSORIAJJLQBEGL2CK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZPTKXI62OPCJCJGCSFMST4HIBQ27J72W/
- http://rhn.redhat.com/errata/RHSA-2016-1080.html
- http://rhn.redhat.com/errata/RHSA-2017-0002.html
- http://www.debian.org/security/2016/dsa-3590
- http://www.ubuntu.com/usn/USN-2960-1
- https://access.redhat.com/errata/RHSA-2017:0879
- https://access.redhat.com/errata/RHSA-2017:0880
- https://access.redhat.com/errata/RHSA-2017:0881
- https://access.redhat.com/errata/RHSA-2017:0882
- https://access.redhat.com/errata/RHSA-2018:0336
