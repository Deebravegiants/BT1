# [C] ALPINE-CVE-2021-41773

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-41773
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-41773
Type: osv

## Affected
- Alpine:v3.11: `apache2` — affected >=0 <2.4.50-r0
- Alpine:v3.12: `apache2` — affected >=0 <2.4.50-r0
- Alpine:v3.13: `apache2` — affected >=0 <2.4.50-r0
- Alpine:v3.14: `apache2` — affected >=0 <2.4.50-r0
- Alpine:v3.15: `apache2` — affected >=0 <2.4.50-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.50-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.50-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.50-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.50-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.50-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.50-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.50-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.50-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.50-r0

## Details
A flaw was found in a change made to path normalization in Apache HTTP Server 2.4.49. An attacker could use a path traversal attack to map URLs to files outside the directories configured by Alias-like directives. If files outside of these directories are not protected by the usual default configuration "require all denied", these requests can succeed. If CGI scripts are also enabled for these aliased pathes, this could allow for remote code execution. This issue is known to be exploited in the wild. This issue only affects Apache 2.4.49 and not earlier versions. The fix in Apache HTTP Server 2.4.50 was found to be incomplete, see CVE-2021-42013.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-41773
