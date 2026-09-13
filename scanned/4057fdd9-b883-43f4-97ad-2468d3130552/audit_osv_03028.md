# [H] ALPINE-CVE-2024-28054

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-28054
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-03-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-28054
Type: osv

## Affected
- Alpine:v3.22: `amavis` — affected >=0 <2.13.1-r0
- Alpine:v3.23: `amavis` — affected >=0 <2.13.1-r0
- Alpine:v3.24: `amavis` — affected >=0 <2.13.1-r0

## Details
Amavis before 2.12.3 and 2.13.x before 2.13.1, in part because of its use of MIME-tools, has an Interpretation Conflict (relative to some mail user agents) when there are multiple boundary parameters in a MIME email message. Consequently, there can be an incorrect check for banned files or malware.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-28054
