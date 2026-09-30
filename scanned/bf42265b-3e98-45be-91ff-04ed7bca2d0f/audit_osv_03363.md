# [H] ALPINE-CVE-2025-61594

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-61594
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-61594
Type: osv

## Affected
- Alpine:v3.20: `ruby` — affected >=0 <3.3.10-r0
- Alpine:v3.21: `ruby` — affected >=0 <3.3.10-r0
- Alpine:v3.23: `ruby` — affected >=0 <3.4.7-r0
- Alpine:v3.24: `ruby` — affected >=0 <3.4.7-r0

## Details
URI is a module providing classes to handle Uniform Resource Identifiers. In versions 0.12.4 and earlier (bundled in Ruby 3.2 series) 0.13.2 and earlier (bundled in Ruby 3.3 series), 1.0.3 and earlier (bundled in Ruby 3.4 series), when using the + operator to combine URIs, sensitive information like passwords from the original URI can be leaked, violating RFC3986 and making applications vulnerable to credential exposure. This is a a bypass for the fix to CVE-2025-27221 that can expose user credentials. This issue has been fixed in versions 0.12.5, 0.13.3 and 1.0.4.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-61594
