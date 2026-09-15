# [H] Logto: SAML IdP injects user-controlled profile attributes raw into signed assertions, allowing privilege escalation at relying Service Providers

## Summary
Severity: High
Advisory: CVE-2026-55789
Aliases: GHSA-vfpw-vq44-4p63
CVSS: 8.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-55789
Type: osv

## Details
Logto is the modern, open-source auth infrastructure for SaaS and AI apps. Prior to 1.41.0, Logto's self-hosted SAML application IdP built the signed SAML response and assertion by string-substituting user-controlled profile attributes such as name, email, and custom attribute-mapping values into element-text placeholders of a SAML XML template using samlify 2.10.0, which left those placeholders unescaped. An authenticated low-privilege user could place XML markup in a profile attribute so Logto signed a forged SAML attribute, such as an arbitrary role, allowing privilege escalation at relying Service Providers that authorize on SAML attributes. This issue is fixed in version 1.41.0.

## References
- https://github.com/logto-io/logto/releases/tag/v1.41.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55789.json
- https://github.com/logto-io/logto/security/advisories/GHSA-vfpw-vq44-4p63
- https://nvd.nist.gov/vuln/detail/CVE-2026-55789
- https://github.com/logto-io/logto/commit/9097054860f0d638d90778d3dcde2ba050b844b6
- https://github.com/logto-io/logto/pull/9107
