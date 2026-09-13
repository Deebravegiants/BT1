# [H] ALPINE-CVE-2021-27922

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-27922
Ecosystem: Alpine:v3.14, Alpine:v3.15
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-27922
Type: osv

## Affected
- Alpine:v3.14: `py3-pillow` — affected >=0 <8.1.2-r0
- Alpine:v3.15: `py3-pillow` — affected >=0 <8.1.2-r0

## Details
Pillow before 8.1.2 allows attackers to cause a denial of service (memory consumption) because the reported size of a contained image is not properly checked for an ICNS container, and thus an attempted memory allocation can be very large.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-27922
