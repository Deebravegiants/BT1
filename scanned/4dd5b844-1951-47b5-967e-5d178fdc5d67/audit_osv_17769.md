# [H] CVE-2020-19492

## Summary
Severity: High
Advisory: CVE-2020-19492
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-07-21
Source: https://osv.dev/vulnerability/CVE-2020-19492
Type: osv

## Details
There is a floating point exception in ReadImage that leads to a Segmentation fault in sam2p 0.49.4. A crafted input will lead to a denial of service or possibly unspecified other impact.

## References
- https://github.com/pts/sam2p/commit/b953f63307c4a83fa4615a4863e3fb250205cd98
- https://github.com/pts/sam2p/issues/66
