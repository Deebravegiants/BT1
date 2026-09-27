# [H] ALPINE-CVE-2017-9798

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-9798
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-09-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-9798
Type: osv

## Affected
- Alpine:v3.10: `apache2` — affected >=0 <2.4.27-r1
- Alpine:v3.11: `apache2` — affected >=0 <2.4.27-r1
- Alpine:v3.12: `apache2` — affected >=0 <2.4.27-r1
- Alpine:v3.13: `apache2` — affected >=0 <2.4.27-r1
- Alpine:v3.14: `apache2` — affected >=0 <2.4.27-r1
- Alpine:v3.15: `apache2` — affected >=0 <2.4.27-r1
- Alpine:v3.16: `apache2` — affected >=0 <2.4.27-r1
- Alpine:v3.17: `apache2` — affected >=0 <2.4.27-r1
- Alpine:v3.18: `apache2` — affected >=0 <2.4.27-r1
- Alpine:v3.19: `apache2` — affected >=0 <2.4.27-r1
- Alpine:v3.20: `apache2` — affected >=0 <2.4.27-r1
- Alpine:v3.21: `apache2` — affected >=0 <2.4.27-r1
- Alpine:v3.22: `apache2` — affected >=0 <2.4.27-r1
- Alpine:v3.23: `apache2` — affected >=0 <2.4.27-r1
- Alpine:v3.24: `apache2` — affected >=0 <2.4.27-r1
- Alpine:v3.3: `apache2` — affected >=0 <2.4.27-r1
- Alpine:v3.4: `apache2` — affected >=0 <2.4.27-r1
- Alpine:v3.5: `apache2` — affected >=0 <2.4.27-r1
- Alpine:v3.6: `apache2` — affected >=0 <2.4.27-r1
- Alpine:v3.7: `apache2` — affected >=0 <2.4.27-r1
- Alpine:v3.8: `apache2` — affected >=0 <2.4.27-r1
- Alpine:v3.9: `apache2` — affected >=0 <2.4.27-r1

## Details
Apache httpd allows remote attackers to read secret data from process memory if the Limit directive can be set in a user's .htaccess file, or if httpd.conf has certain misconfigurations, aka Optionsbleed. This affects the Apache HTTP Server through 2.2.34 and 2.4.x through 2.4.27. The attacker sends an unauthenticated OPTIONS HTTP request when attempting to read secret data. This is a use-after-free issue and thus secret data is not always sent, and the specific data depends on many factors including configuration. Exploitation with .htaccess can be blocked with a patch to the ap_limit_section function in server/core.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-9798
