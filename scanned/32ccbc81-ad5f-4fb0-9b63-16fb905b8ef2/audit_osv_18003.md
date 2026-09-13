# [M] CVE-2020-22674

## Summary
Severity: Medium
Advisory: CVE-2020-22674
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-10-12
Source: https://osv.dev/vulnerability/CVE-2020-22674
Type: osv

## Details
An issue was discovered in gpac 0.8.0. An invalid memory dereference exists in the function FixTrackID located in isom_intern.c, which allows attackers to cause a denial of service (DoS) via a crafted input.

## References
- https://github.com/gpac/gpac/issues/1346
