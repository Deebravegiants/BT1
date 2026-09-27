# [H] ALPINE-CVE-2025-27219

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-27219
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-27219
Type: osv

## Affected
- Alpine:v3.19: `ruby` — affected >=0 <3.2.8-r0
- Alpine:v3.20: `ruby` — affected >=0 <3.3.8-r0
- Alpine:v3.21: `ruby` — affected >=0 <3.3.8-r0
- Alpine:v3.19: `ruby-net-imap` — affected >=0 <0.3.9-r0
- Alpine:v3.20: `ruby-net-imap` — affected >=0 <0.4.19-r0
- Alpine:v3.21: `ruby-net-imap` — affected >=0 <0.4.19-r0

## Details
In the CGI gem before 0.4.2 for Ruby, the CGI::Cookie.parse method in the CGI library contains a potential Denial of Service (DoS) vulnerability. The method does not impose any limit on the length of the raw cookie value it processes. This oversight can lead to excessive resource consumption when parsing extremely large cookies.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-27219
