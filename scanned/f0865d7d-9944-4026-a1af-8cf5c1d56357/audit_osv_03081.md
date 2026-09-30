# [M] ALPINE-CVE-2024-39908

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-39908
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-39908
Type: osv

## Affected
- Alpine:v3.19: `ruby-rexml` — affected >=0 <3.3.9-r0
- Alpine:v3.20: `ruby-rexml` — affected >=0 <3.3.9-r0
- Alpine:v3.21: `ruby-rexml` — affected >=0 <3.3.9-r0
- Alpine:v3.22: `ruby-rexml` — affected >=0 <3.3.9-r0
- Alpine:v3.23: `ruby-rexml` — affected >=0 <3.3.9-r0
- Alpine:v3.24: `ruby-rexml` — affected >=0 <3.3.9-r0

## Details
REXML is an XML toolkit for Ruby. The REXML gem before 3.3.1 has some DoS vulnerabilities when it parses an XML that has many specific characters such as `<`, `0` and `%>`. If you need to parse untrusted XMLs, you many be impacted to these vulnerabilities. The REXML gem 3.3.2 or later include the patches to fix these vulnerabilities. Users are advised to upgrade. Users unable to upgrade should avoid parsing untrusted XML strings.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-39908
