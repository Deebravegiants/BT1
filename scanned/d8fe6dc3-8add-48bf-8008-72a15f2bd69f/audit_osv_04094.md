# [C] Apache HTTP Server weakness with encoded question marks in backreferences

## Summary
Severity: Critical
Advisory: BIT-apache-2024-38474
Aliases: CVE-2024-38474
Ecosystem: Bitnami
Published: 2024-07-03
Source: https://osv.dev/vulnerability/BIT-apache-2024-38474
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.0 <2.4.60

## Details
Substitution encoding issue in mod_rewrite in Apache HTTP Server 2.4.59 and earlier allows attacker to execute scripts in
directories permitted by the configuration but not directly reachable by any URL or source disclosure of scripts meant to only to be executed as CGI.

Users are recommended to upgrade to version 2.4.60, which fixes this issue.

Some RewriteRules that capture and substitute unsafely will now fail unless rewrite flag "UnsafeAllow3F" is specified.

## References
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://security.netapp.com/advisory/ntap-20240712-0001/
- http://www.openwall.com/lists/oss-security/2024/07/01/7
- https://nvd.nist.gov/vuln/detail/CVE-2024-38474
