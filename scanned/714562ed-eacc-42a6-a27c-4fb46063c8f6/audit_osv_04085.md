# [C] Apache HTTP Server: HTTP request splitting with mod_rewrite and mod_proxy

## Summary
Severity: Critical
Advisory: BIT-apache-2023-25690
Aliases: CVE-2023-25690
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-apache-2023-25690
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.0 <2.4.56

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
- http://packetstormsecurity.com/files/176334/Apache-2.4.55-mod_proxy-HTTP-Request-Smuggling.html
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://lists.debian.org/debian-lts-announce/2023/04/msg00028.html
- https://security.gentoo.org/glsa/202309-01
- https://nvd.nist.gov/vuln/detail/CVE-2023-25690
