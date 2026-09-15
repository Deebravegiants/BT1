# [H] CVE-2018-7487

## Summary
Severity: High
Advisory: CVE-2018-7487
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-02-26
Source: https://osv.dev/vulnerability/CVE-2018-7487
Type: osv

## Details
There is a heap-based buffer overflow in the LoadPCX function of in_pcx.cpp in sam2p 0.49.4. A Crafted input will lead to a denial of service or possibly unspecified other impact.

## References
- https://lists.debian.org/debian-lts-announce/2018/04/msg00004.html
- https://github.com/pts/sam2p/issues/18
