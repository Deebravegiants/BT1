# [H] CVE-2020-19491

## Summary
Severity: High
Advisory: CVE-2020-19491
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-07-21
Source: https://osv.dev/vulnerability/CVE-2020-19491
Type: osv

## Details
There is an invalid memory access bug in cgif.c that leads to a Segmentation fault in sam2p 0.49.4. A crafted input will lead to a denial of service or possibly unspecified other impact.

## References
- https://github.com/pts/sam2p/commit/1d62cf8964bfcafa6561c4c3bb66d4aa4c529a73
- https://github.com/pts/sam2p/issues/67
