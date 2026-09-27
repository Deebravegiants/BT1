# [H] CVE-2016-7163

## Summary
Severity: High
Advisory: CVE-2016-7163
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-09-21
Source: https://osv.dev/vulnerability/CVE-2016-7163
Type: osv

## Details
Integer overflow in the opj_pi_create_decode function in pi.c in OpenJPEG allows remote attackers to execute arbitrary code via a crafted JP2 file, which triggers an out-of-bounds read or write.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2T6IQAMS4W65MGP7UW5FPE22PXELTK5D/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/66BWMMMWXH32J5AOGLAJGZA3GH5LZHXH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AQ2IIIQSJ3J4MONBOGCG6XHLKKJX2HKM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/H4IRSGYMBSHCBZP23CUDIRJ3LBKH6ZJ7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JYLOX7PZS3ZUHQ6RGI3M6H27B7I5ZZ26/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YGKSEWWWED77Q5ZHK4OA2EKSJXLRU3MK/
- http://rhn.redhat.com/errata/RHSA-2017-0559.html
- http://rhn.redhat.com/errata/RHSA-2017-0838.html
- http://www.debian.org/security/2016/dsa-3665
- http://www.openwall.com/lists/oss-security/2016/09/08/3
- http://www.openwall.com/lists/oss-security/2016/09/08/6
- http://www.securityfocus.com/bid/92897
- https://github.com/uclouvain/openjpeg/commit/c16bc057ba3f125051c9966cf1f5b68a05681de4
- https://github.com/uclouvain/openjpeg/commit/ef01f18dfc6780b776d0674ed3e7415c6ef54d24
- https://github.com/uclouvain/openjpeg/issues/826
- https://github.com/uclouvain/openjpeg/pull/809
