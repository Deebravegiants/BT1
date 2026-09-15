# [M] CVE-2022-35434

## Summary
Severity: Medium
Advisory: CVE-2022-35434
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-08-16
Source: https://osv.dev/vulnerability/CVE-2022-35434
Type: osv

## Details
jpeg-quantsmooth before commit 8879454 contained a floating point exception (FPE) via /jpeg-quantsmooth/jpegqs+0x4f5d6c.

## References
- https://github.com/ilyakurdyukov/jpeg-quantsmooth/issues/25
