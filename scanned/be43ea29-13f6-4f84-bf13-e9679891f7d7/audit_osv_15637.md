# [H] CVE-2019-18218

## Summary
Severity: High
Advisory: CVE-2019-18218
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-10-21
Source: https://osv.dev/vulnerability/CVE-2019-18218
Type: osv

## Details
cdf_read_property_info in cdf.c in file through 5.37 does not restrict the number of CDF_VECTOR elements, which allows a heap-based buffer overflow (4-byte out-of-bounds write).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CV6PFCEYHYALMTT45QE2U5C5TEJZQPXJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/D6BJVGXSCC6NMIAWX36FPWHEIFON3OSE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VBK6XOJR6OVWT2FUEBO7V7KCOSSLAP52/
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00044.html
- https://lists.debian.org/debian-lts-announce/2019/10/msg00032.html
- https://lists.debian.org/debian-lts-announce/2021/07/msg00008.html
- https://security.gentoo.org/glsa/202003-24
- https://security.netapp.com/advisory/ntap-20200115-0001/
- https://usn.ubuntu.com/4172-1/
- https://usn.ubuntu.com/4172-2/
- https://www.debian.org/security/2019/dsa-4550
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=16780
- https://github.com/file/file/commit/46a8443f76cec4b41ec736eca396984c74664f84
