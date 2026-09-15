# [H] Incorrect Authorization in SimGear

## Summary
Severity: High
Advisory: CVE-2025-0781
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2025-01-28
Source: https://osv.dev/vulnerability/CVE-2025-0781
Type: osv

## Details
An attacker can bypass the sandboxing of Nasal scripts and arbitrarily write to any file path that the user has permission to modify at the operating-system level.

## References
- https://lists.debian.org/debian-lts-announce/2025/01/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00029.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/0xxx/CVE-2025-0781.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-0781
- https://gitlab.com/flightgear/flightgear/-/issues/3025
- https://gitlab.com/flightgear/flightgear/-/commit/ad37afce28083fad7f79467b3ffdead753584358
- https://gitlab.com/flightgear/simgear/-/commit/5bb023647114267141a7610e8f1ca7d6f4f5a5a8
