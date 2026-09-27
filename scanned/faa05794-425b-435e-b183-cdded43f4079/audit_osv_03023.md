# [M] ALPINE-CVE-2024-27281

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-27281
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.5 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-05-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-27281
Type: osv

## Affected
- Alpine:v3.16: `ruby` — affected >=0 <3.1.5-r0
- Alpine:v3.17: `ruby` — affected >=0 <3.1.5-r0
- Alpine:v3.18: `ruby` — affected >=0 <3.2.4-r0
- Alpine:v3.19: `ruby` — affected >=0 <3.2.4-r0
- Alpine:v3.20: `ruby` — affected >=0 <3.3.1-r0
- Alpine:v3.21: `ruby` — affected >=0 <3.3.1-r0
- Alpine:v3.22: `ruby` — affected >=0 <3.3.1-r0
- Alpine:v3.23: `ruby` — affected >=0 <3.3.1-r0
- Alpine:v3.24: `ruby` — affected >=0 <3.3.1-r0

## Details
An issue was discovered in RDoc 6.3.3 through 6.6.2, as distributed in Ruby 3.x through 3.3.0. When parsing .rdoc_options (used for configuration in RDoc) as a YAML file, object injection and resultant remote code execution are possible because there are no restrictions on the classes that can be restored. (When loading the documentation cache, object injection and resultant remote code execution are also possible if there were a crafted cache.) The main fixed version is 6.6.3.1. For Ruby 3.0 users, a fixed version is rdoc 6.3.4.1. For Ruby 3.1 users, a fixed version is rdoc 6.4.1.1. For Ruby 3.2 users, a fixed version is rdoc 6.5.1.1.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-27281
