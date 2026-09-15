# [M] n8n: Per-Resource OAuth Consent Bypass via Unbound Refresh Token Resource Substitution

## Summary
Severity: Medium
Advisory: CVE-2026-86073
Aliases: GHSA-cw9w-vv67-hf73
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:L/VA:L/SC:N/SI:N/SA:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-86073
Type: osv

## Details
n8n is an open source workflow automation platform. Prior to 2.37.7 and 2.38.1, the OAuth token endpoint bound an authorization code's first access token to the consented resource but did not bind its refresh token. Refreshing checked only that the requested resource was registered, not that it matched the original grant. An OAuth client approved for one workflow could substitute a different workflow URL in the resource parameter and obtain a valid token for an unapproved workflow accessible to the consenting user. This issue is fixed in versions 2.37.7 and 2.38.1.

## References
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.37.7
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.38.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86073.json
- https://github.com/n8n-io/n8n/security/advisories/GHSA-cw9w-vv67-hf73
- https://nvd.nist.gov/vuln/detail/CVE-2026-86073
- https://github.com/n8n-io/n8n/commit/18458482861097a26f874f30ad7e8136e268475c
- https://github.com/n8n-io/n8n/commit/380788fd9a3264c83161e868026a98731d274d88
- https://github.com/n8n-io/n8n/pull/37122
- https://github.com/n8n-io/n8n/pull/37588
