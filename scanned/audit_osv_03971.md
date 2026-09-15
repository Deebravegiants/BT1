# [H] ALPINE-CVE-2026-82209

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-82209
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-09-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-82209
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=0 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=0 <8.22.0-r0

## Details
When libpsl support is enabled, libcurl fails to enforce the Public Suffix
List boundary check when processing a `Set-Cookie` header where the `Domain`
attribute explicitly matches an origin host that is itself a public suffix
(e.g., `Domain=co.uk` set by `co.uk`).

Instead of coercing it into a strict host-only cookie, libcurl saves the
cookie with wildcard domain scope (`.co.uk`). Consequently, the cookie is
inappropriately included in subsequent outbound requests or HTTP redirects to
arbitrary sibling subdomains under the same public suffix (e.g.,
`attacker.co.uk`).

## References
- https://security.alpinelinux.org/vuln/CVE-2026-82209
