# [M] n8n: Unauthenticated Persistent Storage Exhaustion via OAuth Dynamic Client Registration Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-86075
Aliases: GHSA-hh89-3r9w-qj3j
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-86075
Type: osv

## Details
n8n is an open source workflow automation platform. Prior to 2.37.7 and 2.38.2, the OAuth Dynamic Client Registration endpoint bounded redirect_uris but accepted arbitrarily large client_name and grant_types values. An unauthenticated remote caller could repeatedly persist oversized values in oauth_clients and exhaust database storage. The affected validation is in packages/cli/src/modules/oauth-server/oauth-server.service.ts, including MAX_CLIENT_NAME_LENGTH and MAX_GRANT_TYPES. This issue is fixed in versions 2.37.7 and 2.38.2.

## References
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.37.7
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.38.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86075.json
- https://github.com/n8n-io/n8n/security/advisories/GHSA-hh89-3r9w-qj3j
- https://nvd.nist.gov/vuln/detail/CVE-2026-86075
