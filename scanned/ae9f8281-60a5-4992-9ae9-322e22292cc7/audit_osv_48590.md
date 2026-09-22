# [M] CVE-2017-9870

## Summary
Severity: Medium
Advisory: CVE-2017-9870
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-25
Source: https://osv.dev/vulnerability/CVE-2017-9870
Type: osv

## Details
The III_i_stereo function in layer3.c in mpglib, as used in libmpgdecoder.a in LAME 3.99.5 and other products, allows remote attackers to cause a denial of service (buffer over-read and application crash) via a crafted audio file that is mishandled in the code for the "block_type == 2" case, a similar issue to CVE-2017-11126.

## References
- http://www.securityfocus.com/bid/99287
- https://blogs.gentoo.org/ago/2017/06/17/lame-global-buffer-overflow-in-iii_i_stereo-layer3-c/
