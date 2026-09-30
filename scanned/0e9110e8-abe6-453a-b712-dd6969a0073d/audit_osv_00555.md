# [H] ALPINE-CVE-2017-15710

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-15710
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-15710
Type: osv

## Affected
- Alpine:v3.10: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.11: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.12: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.13: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.14: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.15: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.4: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.5: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.6: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.7: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.8: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.9: `apache2` — affected >=0 <2.4.33-r0

## Details
In Apache httpd 2.0.23 to 2.0.65, 2.2.0 to 2.2.34, and 2.4.0 to 2.4.29, mod_authnz_ldap, if configured with AuthLDAPCharsetConfig, uses the Accept-Language header value to lookup the right charset encoding when verifying the user's credentials. If the header value is not present in the charset conversion table, a fallback mechanism is used to truncate it to a two characters value to allow a quick retry (for example, 'en-US' is truncated to 'en'). A header value of less than two characters forces an out of bound write of one NUL byte to a memory location that is not part of the string. In the worst case, quite unlikely, the process would crash which could be used as a Denial of Service attack. In the more likely case, this memory is already reserved for future use and the issue has no effect at all.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-15710
