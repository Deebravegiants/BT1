# [H] CVE-2018-11489

## Summary
Severity: High
Advisory: CVE-2018-11489
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-05-26
Source: https://osv.dev/vulnerability/CVE-2018-11489
Type: osv

## Details
The DGifDecompressLine function in dgif_lib.c in GIFLIB (possibly version 3.0.x), as later shipped in cgif.c in sam2p 0.49.4, has a heap-based buffer overflow because a certain CrntCode array index is not checked. This will lead to a denial of service or possibly unspecified other impact.

## References
- https://lists.apache.org/thread.html/rf9fa47ab66495c78bb4120b0754dd9531ca2ff0430f6685ac9b07772%40%3Cdev.mina.apache.org%3E
- http://www.securityfocus.com/bid/104341
- https://github.com/pts/sam2p/issues/37
