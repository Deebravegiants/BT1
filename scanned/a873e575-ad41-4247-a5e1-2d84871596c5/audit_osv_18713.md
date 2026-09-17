# [M] CVE-2020-35534

## Summary
Severity: Medium
Advisory: CVE-2020-35534
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-09-01
Source: https://osv.dev/vulnerability/CVE-2020-35534
Type: osv

## Details
In LibRaw, there is a memory corruption vulnerability within the "crxFreeSubbandData()" function (libraw\src\decoders\crx.cpp) when processing cr3 files.

## References
- https://github.com/LibRaw/LibRaw/commit/e41f331e90b383e3208cefb74e006df44bf3a4b8
- https://github.com/LibRaw/LibRaw/issues/279
