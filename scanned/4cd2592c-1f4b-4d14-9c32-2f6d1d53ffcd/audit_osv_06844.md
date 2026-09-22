# [M] ModSecurity empty XML tag causes segmentation fault

## Summary
Severity: Medium
Advisory: BIT-modsecurity-2025-52891
Aliases: BIT-modsecurity2-2025-52891, CVE-2025-52891, GHSA-gw9c-4wfm-vj3x
Ecosystem: Bitnami
Published: 2025-07-04
Source: https://osv.dev/vulnerability/BIT-modsecurity-2025-52891
Type: osv

## Affected
- Bitnami: `modsecurity` — affected >=2.9.8 <3.0.12

## Details
ModSecurity is an open source, cross platform web application firewall (WAF) engine for Apache, IIS and Nginx. In versions 2.9.8 to before 2.9.11, an empty XML tag can cause a segmentation fault. If SecParseXmlIntoArgs is set to On or OnlyArgs, and the request type is application/xml, and at least one XML tag is empty (eg <foo></foo>), then a segmentation fault occurs. This issue has been patched in version 2.9.11. A workaround involves setting SecParseXmlIntoArgs to Off.

## References
- https://github.com/owasp-modsecurity/ModSecurity/commit/ecd7b9736836eee391d25f35d5bd06a3ce35a45d
- https://github.com/owasp-modsecurity/ModSecurity/security/advisories/GHSA-gw9c-4wfm-vj3x
- https://nvd.nist.gov/vuln/detail/CVE-2025-52891
