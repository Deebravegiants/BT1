# [H] CVE-2019-16056

## Summary
Severity: High
Advisory: CVE-2019-16056
Aliases: PSF-2019-5
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-09-06
Source: https://osv.dev/vulnerability/CVE-2019-16056
Type: osv

## Details
An issue was discovered in Python through 2.7.16, 3.x through 3.5.7, 3.6.x through 3.6.9, and 3.7.x through 3.7.4. The email module wrongly parses email addresses that contain multiple @ characters. An application that uses the email module and implements some kind of checks on the From/To headers of a message could be tricked into accepting an email address that should be denied. An attack may be the same as in CVE-2019-11340; however, this CVE applies to Python more generally.

## References
- https://lists.apache.org/thread.html/r1b103833cb5bc8466e24ff0ecc5e75b45a705334ab6a444e64e840a0%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4X3HW5JRZ7GCPSR7UHJOLD7AWLTQCDVR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BEARDOTXCYPYELKBD2KWZ27GSPXDI3GQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/COATURTCY7G67AYI6UDV5B2JZTBCKIDX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/E2HP37NUVLQSBW3J735A2DQDOZ4ZGBLY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ER6LONC2B2WYIO56GBQUDU6QTWZDPUNQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JCPGLTTOBB3QEARDX4JOYURP6ELNNA2V/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/K4KZEFP6E4YPYB52AF4WXCUDSGQOTF37/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/K7HNVIFMETMFWWWUNTB72KYJYXCZOS5V/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M34WOYCDKTDE5KLUACE2YIEH7D37KHRX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NF3DRDGMVIRYNZMSLJIHNW47HOUQYXVG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OYGESQSGIHDCIGOBVF7VXCMIE6YDWRYB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QASRD4E2G65GGEHYKVHYCXB2XWAGTNL4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QP46PQSUKYPGWTADQ67NOV3BUN6JM34Z/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SDQQ56P7ZZR64XV5DUVWNSNXKKEXUG2J/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZBTGPBUABGXZ7WH7677OEM3NSP6ZEA76/
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00062.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00063.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00021.html
