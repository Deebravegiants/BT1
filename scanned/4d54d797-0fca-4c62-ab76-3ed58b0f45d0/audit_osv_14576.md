# [C] CVE-2019-10160

## Summary
Severity: Critical
Advisory: CVE-2019-10160
Aliases: PSF-2019-3
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-07
Source: https://osv.dev/vulnerability/CVE-2019-10160
Type: osv

## Details
A security regression of CVE-2019-9636 was discovered in python since commit d537ab0ff9767ef024f26246899728f0116b1ec3 affecting versions 2.7, 3.5, 3.6, 3.7 and from v3.8.0a4 through v3.8.0b1, which still allows an attacker to exploit CVE-2019-9636 by abusing the user and password parts of a URL. When an application parses user-supplied URLs to store cookies, authentication credentials, or other kind of information, it is possible for an attacker to provide specially crafted URLs to make the application locate host-related information (e.g. cookies, authentication data) and send them to a different host than where it should, unlike if the URLs had been correctly parsed. The result of an attack may vary based on the application.

## References
- https://lists.apache.org/thread.html/r1b103833cb5bc8466e24ff0ecc5e75b45a705334ab6a444e64e840a0%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2ORNTF62QPLMJXIQ7KTZQ2776LMIXEKL/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/44TS66GJMO5H3RLMVZEBGEFTB6O2LJJU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4X3HW5JRZ7GCPSR7UHJOLD7AWLTQCDVR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/E2HP37NUVLQSBW3J735A2DQDOZ4ZGBLY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ER6LONC2B2WYIO56GBQUDU6QTWZDPUNQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HQEQLXLOCR3SNM3AA5RRYJFQ5AZBYJ4L/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JCPGLTTOBB3QEARDX4JOYURP6ELNNA2V/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KRYFIMISZ47NTAU3XWZUOFB7CYL62KES/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M34WOYCDKTDE5KLUACE2YIEH7D37KHRX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NF3DRDGMVIRYNZMSLJIHNW47HOUQYXVG/
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00042.html
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00040.html
- https://access.redhat.com/errata/RHSA-2019:1587
- https://access.redhat.com/errata/RHSA-2019:1700
- https://access.redhat.com/errata/RHSA-2019:2437
- https://lists.debian.org/debian-lts-announce/2019/06/msg00022.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00011.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00034.html
- https://security.netapp.com/advisory/ntap-20190617-0003/
