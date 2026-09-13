# [C] ALPINE-CVE-2023-25690

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2023-25690
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-25690
Type: osv

## Affected
- Alpine:v3.14: `apache2` — affected >=0 <2.4.56-r0
- Alpine:v3.15: `apache2` — affected >=0 <2.4.56-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.56-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.56-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.56-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.56-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.56-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.56-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.56-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.56-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.56-r0

## Details
Some mod_proxy configurations on Apache HTTP Server versions 2.4.0 through 2.4.55 allow a HTTP Request Smuggling attack.




Configurations are affected when mod_proxy is enabled along with some form of RewriteRule
 or ProxyPassMatch in which a non-specific pattern matches
 some portion of the user-supplied request-target (URL) data and is then
 re-inserted into the proxied request-target using variable 
substitution. For example, something like:




RewriteEngine on
RewriteRule "^/here/(.*)" "http://example.com:8080/elsewhere?$1"; [P]
ProxyPassReverse /here/ http://example.com:8080/


Request splitting/smuggling could result in bypass of access controls in the proxy server, proxying unintended URLs to existing origin servers, and cache poisoning. Users are recommended to update to at least version 2.4.56 of Apache HTTP Server.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-25690
