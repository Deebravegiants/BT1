# [M] ALPINE-CVE-2025-58767

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-58767
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-58767
Type: osv

## Affected
- Alpine:v3.23: `ruby-rexml` — affected >=3.3.3 <3.4.4-r0
- Alpine:v3.24: `ruby-rexml` — affected >=3.3.3 <3.4.4-r0

## Details
REXML is an XML toolkit for Ruby. The REXML gems from 3.3.3 to 3.4.1 has a DoS vulnerability when parsing XML containing multiple XML declarations. If you need to parse untrusted XMLs, you may be impacted to these vulnerabilities. The REXML gem 3.4.2 or later include the patches to fix these vulnerabilities.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-58767
