# [M] CVE-2017-9869

## Summary
Severity: Medium
Advisory: CVE-2017-9869
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-25
Source: https://osv.dev/vulnerability/CVE-2017-9869
Type: osv

## Details
The II_step_one function in layer2.c in mpglib, as used in libmpgdecoder.a in LAME 3.99.5 and other products, allows remote attackers to cause a denial of service (buffer over-read and application crash) via a crafted audio file.

## References
- https://www.exploit-db.com/exploits/42258/
- http://www.securityfocus.com/bid/99272
- https://blogs.gentoo.org/ago/2017/06/17/lame-global-buffer-overflow-in-ii_step_one-layer2-c/
