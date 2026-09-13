# [C] Apache HTTP Server weakness in mod_rewrite when first segment of substitution matches filesystem path.

## Summary
Severity: Critical
Advisory: BIT-apache-2024-38475
Aliases: CVE-2024-38475
Ecosystem: Bitnami
Published: 2024-07-03
Source: https://osv.dev/vulnerability/BIT-apache-2024-38475
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.0 <2.4.60

## Details
Improper escaping of output in mod_rewrite in Apache HTTP Server 2.4.59 and earlier allows an attacker to map URLs to filesystem locations that are permitted to be served by the server but are not intentionally/directly reachable by any URL, resulting in code execution or source code disclosure. 

Substitutions in server context that use a backreferences or variables as the first segment of the substitution are affected.  Some unsafe RewiteRules will be broken by this change and the rewrite flag "UnsafePrefixStat" can be used to opt back in once ensuring the substitution is appropriately constrained.

## References
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://security.netapp.com/advisory/ntap-20240712-0001/
- http://www.openwall.com/lists/oss-security/2024/07/01/8
- https://github.com/apache/httpd/commit/9a6157d1e2f7ab15963020381054b48782bc18cf
- https://www.blackhat.com/us-24/briefings/schedule/index.html#confusion-attacks-exploiting-hidden-semantic-ambiguity-in-apache-http-server-pre-recorded-40227
- https://nvd.nist.gov/vuln/detail/CVE-2024-38475
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2024-38475
- https://psirt.global.sonicwall.com/vuln-detail/SNWLID-2024-0018
