# [H] CVE-2018-11490

## Summary
Severity: High
Advisory: CVE-2018-11490
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-05-26
Source: https://osv.dev/vulnerability/CVE-2018-11490
Type: osv

## Details
The DGifDecompressLine function in dgif_lib.c in GIFLIB (possibly version 3.0.x), as later shipped in cgif.c in sam2p 0.49.4, has a heap-based buffer overflow because a certain "Private->RunningCode - 2" array index is not checked. This will lead to a denial of service or possibly unspecified other impact.

## References
- http://www.securityfocus.com/bid/104327
- https://github.com/pts/sam2p/issues/38
- https://lists.debian.org/debian-lts-announce/2022/12/msg00008.html
- https://usn.ubuntu.com/4107-1/
