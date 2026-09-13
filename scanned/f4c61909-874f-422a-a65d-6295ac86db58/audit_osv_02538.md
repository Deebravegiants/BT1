# [C] ALPINE-CVE-2022-29361

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-29361
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-05-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-29361
Type: osv

## Affected
- Alpine:v3.23: `py3-werkzeug` — affected >=0 <2.2.2-r0
- Alpine:v3.24: `py3-werkzeug` — affected >=0 <2.2.2-r0

## Details
Improper parsing of HTTP requests in Pallets Werkzeug v2.1.0 and below allows attackers to perform HTTP Request Smuggling using a crafted HTTP request with multiple requests included inside the body. NOTE: the vendor's position is that this behavior can only occur in unsupported configurations involving development mode and an HTTP server from outside the Werkzeug project

## References
- https://security.alpinelinux.org/vuln/CVE-2022-29361
