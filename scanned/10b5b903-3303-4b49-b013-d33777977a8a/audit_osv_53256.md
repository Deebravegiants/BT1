# [M] CVE-2022-35064

## Summary
Severity: Medium
Advisory: CVE-2022-35064
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-09-19
Source: https://osv.dev/vulnerability/CVE-2022-35064
Type: osv

## Details
OTFCC commit 617837b was discovered to contain a heap buffer overflow via /release-x64/otfccdump+0x4adcdb in __asan_memset.

## References
- https://drive.google.com/file/d/1btOL19V9nmB4BCUBSQ2fViABe3tMZ8mp/view?usp=sharing
- https://github.com/Cvjark/Poc/blob/main/otfcc/CVE-2022-35064.md
