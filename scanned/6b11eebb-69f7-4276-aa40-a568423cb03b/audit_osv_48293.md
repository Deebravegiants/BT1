# [M] CVE-2017-5834

## Summary
Severity: Medium
Advisory: CVE-2017-5834
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-03
Source: https://osv.dev/vulnerability/CVE-2017-5834
Type: osv

## Details
The parse_dict_node function in bplist.c in libplist allows attackers to cause a denial of service (out-of-bounds heap read and crash) via a crafted file.

## References
- https://lists.debian.org/debian-lts-announce/2020/04/msg00002.html
- http://www.securityfocus.com/bid/96022
- http://www.openwall.com/lists/oss-security/2017/01/31/6
- http://www.openwall.com/lists/oss-security/2017/02/02/4
- https://github.com/libimobiledevice/libplist/issues/89
