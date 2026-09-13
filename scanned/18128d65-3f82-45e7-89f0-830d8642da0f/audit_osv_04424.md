# [M] Insufficient control of custom field value sizes

## Summary
Severity: Medium
Advisory: BIT-discourse-2024-21655
Aliases: CVE-2024-21655, GHSA-m5fc-94mm-38fx
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2024-21655
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.1.4

## Details
Discourse is a platform for community discussion. For fields that are client editable, limits on sizes are not imposed. This allows a malicious actor to cause a Discourse instance to use excessive disk space and also often excessive bandwidth. The issue is patched 3.1.4 and 3.2.0.beta4.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-m5fc-94mm-38fx
- https://nvd.nist.gov/vuln/detail/CVE-2024-21655
