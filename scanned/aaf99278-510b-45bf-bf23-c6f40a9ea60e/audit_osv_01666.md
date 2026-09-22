# [M] ALPINE-CVE-2019-9325

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-9325
Ecosystem: Alpine:v3.11
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2019-09-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-9325
Type: osv

## Affected
- Alpine:v3.11: `libvpx` — affected >=0 <1.8.1-r0

## Details
In libvpx, there is a possible out of bounds read due to a missing bounds check. This could lead to remote information disclosure with no additional execution privileges needed. User interaction is needed for exploitation. Product: AndroidVersions: Android-10Android ID: A-112001302

## References
- https://security.alpinelinux.org/vuln/CVE-2019-9325
