# [M] n8n: Disabled OIDC SSO Endpoints Remain Active and Issue Valid Sessions

## Summary
Severity: Medium
Advisory: CVE-2026-86084
Aliases: GHSA-pf83-w3f9-8m37
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-86084
Type: osv

## Details
n8n is an open source workflow automation platform. Prior to 1.123.76, 2.37.7, and 2.38.2, the public OIDC login and callback endpoints completed authentication even when OIDC was not the enabled active authentication method. An Enterprise administrator who had configured and later disabled an identity provider still exposed a working route that could issue valid sessions. The affected logic is packages/cli/src/modules/sso-oidc/oidc.service.ee.ts, including generateLoginUrl and the callback flow that lacked assertOidcLoginEnabled. This issue is fixed in versions 1.123.76, 2.37.7 and 2.38.2.

## References
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.76
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.37.7
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.38.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86084.json
- https://github.com/n8n-io/n8n/security/advisories/GHSA-pf83-w3f9-8m37
- https://nvd.nist.gov/vuln/detail/CVE-2026-86084
