# [M] CVE-2016-7477

## Summary
Severity: Medium
Advisory: CVE-2016-7477
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-15
Source: https://osv.dev/vulnerability/CVE-2016-7477
Type: osv

## Details
The ff_put_pixels8_xy2_mmx function in rnd_template.c in Libav 11.7 allows remote attackers to cause a denial of service (invalid memory access and crash) via a crafted mp3 file.  NOTE: this issue was originally reported as involving a NULL pointer dereference.

## References
- http://www.openwall.com/lists/oss-security/2016/09/21/6
- http://www.securityfocus.com/bid/93042
- https://blogs.gentoo.org/ago/2016/09/20/libav-null-pointer-dereference-in-ff_put_pixels8_xy2_mmx-rnd_template-c/
