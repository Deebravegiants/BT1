# [M] CVE-2016-7393

## Summary
Severity: Medium
Advisory: CVE-2016-7393
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-15
Source: https://osv.dev/vulnerability/CVE-2016-7393
Type: osv

## Details
Stack-based buffer overflow in the aac_sync function in aac_parser.c in Libav before 11.5 allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted file.

## References
- https://git.libav.org/?p=libav.git%3Ba=commit%3Bh=fb1473080223a634b8ac2cca48a632d037a0a69d
- http://www.securityfocus.com/bid/92902
- http://www.openwall.com/lists/oss-security/2016/09/10/5
- https://blogs.gentoo.org/ago/2016/08/20/libav-stack-based-buffer-overflow-in-aac_sync-aac_parser-c/
