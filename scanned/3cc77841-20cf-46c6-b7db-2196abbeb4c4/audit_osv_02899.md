# [M] ALPINE-CVE-2023-46218

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-46218
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2023-12-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-46218
Type: osv

## Affected
- Alpine:v3.15: `curl` — affected >=7.46.0 <8.5.0-r0
- Alpine:v3.16: `curl` — affected >=7.46.0 <8.5.0-r0
- Alpine:v3.17: `curl` — affected >=7.46.0 <8.5.0-r0
- Alpine:v3.18: `curl` — affected >=7.46.0 <8.5.0-r0
- Alpine:v3.19: `curl` — affected >=7.46.0 <8.5.0-r0
- Alpine:v3.20: `curl` — affected >=7.46.0 <8.5.0-r0
- Alpine:v3.21: `curl` — affected >=7.46.0 <8.5.0-r0
- Alpine:v3.22: `curl` — affected >=7.46.0 <8.5.0-r0
- Alpine:v3.23: `curl` — affected >=7.46.0 <8.5.0-r0
- Alpine:v3.24: `curl` — affected >=7.46.0 <8.5.0-r0

## Details
This flaw allows a malicious HTTP server to set "super cookies" in curl that
are then passed back to more origins than what is otherwise allowed or
possible. This allows a site to set cookies that then would get sent to
different and unrelated sites and domains.

It could do this by exploiting a mixed case flaw in curl's function that
verifies a given cookie domain against the Public Suffix List (PSL). For
example a cookie could be set with `domain=co.UK` when the URL used a lower
case hostname `curl.co.uk`, even though `co.uk` is listed as a PSL domain.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-46218
