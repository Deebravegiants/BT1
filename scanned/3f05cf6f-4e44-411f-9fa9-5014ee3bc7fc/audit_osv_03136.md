# [H] ALPINE-CVE-2024-49761

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-49761
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-49761
Type: osv

## Affected
- Alpine:v3.19: `ruby-rexml` — affected >=0 <3.3.9-r0
- Alpine:v3.20: `ruby-rexml` — affected >=0 <3.3.9-r0
- Alpine:v3.21: `ruby-rexml` — affected >=0 <3.3.9-r0
- Alpine:v3.22: `ruby-rexml` — affected >=0 <3.3.9-r0
- Alpine:v3.23: `ruby-rexml` — affected >=0 <3.3.9-r0
- Alpine:v3.24: `ruby-rexml` — affected >=0 <3.3.9-r0

## Details
REXML is an XML toolkit for Ruby. The REXML gem before 3.3.9 has a ReDoS vulnerability when it parses an XML that has many digits between &# and x...; in a hex numeric character reference (&#x...;). This does not happen with Ruby 3.2 or later. Ruby 3.1 is the only affected maintained Ruby. The REXML gem 3.3.9 or later include the patch to fix the vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-49761
