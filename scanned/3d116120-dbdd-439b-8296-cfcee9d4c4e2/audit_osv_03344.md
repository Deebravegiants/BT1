# [H] ALPINE-CVE-2025-58145

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-58145
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-58145
Type: osv

## Affected
- Alpine:v3.19: `xen` — affected >=4.12.0 <4.18.5-r2
- Alpine:v3.20: `xen` — affected >=4.12.0 <4.18.5-r2
- Alpine:v3.21: `xen` — affected >=4.12.0 <4.19.3-r1
- Alpine:v3.22: `xen` — affected >=4.12.0 <4.20.1-r1
- Alpine:v3.23: `xen` — affected >=4.12.0 <4.20.1-r1
- Alpine:v3.24: `xen` — affected >=4.12.0 <4.20.1-r1

## Details
[This CNA information record relates to multiple CVEs; the
text explains which aspects/vulnerabilities correspond to which CVE.]

There are two issues related to the mapping of pages belonging to other
domains: For one, an assertion is wrong there, where the case actually
needs handling.  A NULL pointer de-reference could result on a release
build.  This is CVE-2025-58144.

And then the P2M lock isn't held until a page reference was actually
obtained (or the attempt to do so has failed).  Otherwise the page can
not only change type, but even ownership in between, thus allowing
domain boundaries to be violated.  This is CVE-2025-58145.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-58145
