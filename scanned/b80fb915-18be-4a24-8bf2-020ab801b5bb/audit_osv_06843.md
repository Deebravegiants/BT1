# [H] ModSecurity Has Possible DoS Vulnerability

## Summary
Severity: High
Advisory: BIT-modsecurity-2025-47947
Aliases: BIT-modsecurity2-2025-47947, CVE-2025-47947, GHSA-859r-vvv8-rm8r
Ecosystem: Bitnami
Published: 2025-05-26
Source: https://osv.dev/vulnerability/BIT-modsecurity-2025-47947
Type: osv

## Affected
- Bitnami: `modsecurity` — affected >=0 <3.0.12

## Details
ModSecurity is an open source, cross platform web application firewall (WAF) engine for Apache, IIS and Nginx. Versions up to and including 2.9.8 are vulnerable to denial of service in one special case (in stable released versions): when the payload's content type is `application/json`, and there is at least one rule which does a `sanitiseMatchedBytes` action. A patch is available at pull request 3389 and expected to be part of version 2.9.9. No known workarounds are available.

## References
- https://github.com/owasp-modsecurity/ModSecurity/pull/3389
- https://github.com/owasp-modsecurity/ModSecurity/security/advisories/GHSA-859r-vvv8-rm8r
- https://nvd.nist.gov/vuln/detail/CVE-2025-47947
