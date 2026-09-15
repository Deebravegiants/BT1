# [H] Apache HTTP Server: mod_rewrite proxy handler substitution

## Summary
Severity: High
Advisory: BIT-apache-2024-39573
Aliases: CVE-2024-39573
Ecosystem: Bitnami
Published: 2024-07-03
Source: https://osv.dev/vulnerability/BIT-apache-2024-39573
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.0 <2.4.60

## Details
Potential SSRF in mod_rewrite in Apache HTTP Server 2.4.59 and earlier allows an attacker to cause unsafe RewriteRules to unexpectedly setup URL's to be handled by mod_proxy.
Users are recommended to upgrade to version 2.4.60, which fixes this issue.

## References
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://security.netapp.com/advisory/ntap-20240712-0001/
- http://www.openwall.com/lists/oss-security/2024/07/01/11
- https://nvd.nist.gov/vuln/detail/CVE-2024-39573
- http://seclists.org/fulldisclosure/2024/Oct/11
