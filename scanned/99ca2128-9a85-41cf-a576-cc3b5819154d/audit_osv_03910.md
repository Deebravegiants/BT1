# [M] ALPINE-CVE-2026-6429

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-6429
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-6429
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=7.14.0 <8.20.0-r0
- Alpine:v3.24: `curl` — affected >=7.14.0 <8.20.0-r0

## Details
When asked to both use a `.netrc` file for credentials and to follow HTTP
redirects, libcurl could leak the password used for the first host to the
followed-to host under certain circumstances.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-6429
