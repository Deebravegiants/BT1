# [M] ALPINE-CVE-2024-43398

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-43398
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-08-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-43398
Type: osv

## Affected
- Alpine:v3.19: `ruby-rexml` — affected >=0 <3.3.9-r0
- Alpine:v3.20: `ruby-rexml` — affected >=0 <3.3.9-r0
- Alpine:v3.21: `ruby-rexml` — affected >=0 <3.3.9-r0
- Alpine:v3.22: `ruby-rexml` — affected >=0 <3.3.9-r0
- Alpine:v3.23: `ruby-rexml` — affected >=0 <3.3.9-r0
- Alpine:v3.24: `ruby-rexml` — affected >=0 <3.3.9-r0

## Details
REXML is an XML toolkit for Ruby. The REXML gem before 3.3.6 has a DoS vulnerability when it parses an XML that has many deep elements that have same local name attributes. If you need to parse untrusted XMLs with tree parser API like REXML::Document.new, you may be impacted to this vulnerability. If you use other parser APIs such as stream parser API and SAX2 parser API, this vulnerability is not affected. The REXML gem 3.3.6 or later include the patch to fix the vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-43398
