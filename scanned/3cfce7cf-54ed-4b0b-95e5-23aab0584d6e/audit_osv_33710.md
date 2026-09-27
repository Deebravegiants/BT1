# [M] Wasp has case insensitive OAuth ID vulnerability

## Summary
Severity: Medium
Advisory: CVE-2025-49006
Aliases: GHSA-qvjc-6xv7-6v5f
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2025-06-09
Source: https://osv.dev/vulnerability/CVE-2025-49006
Type: osv

## Details
Wasp (Web Application Specification) is a Rails-like framework for React, Node.js, and Prisma. Prior to version 0.16.6, Wasp authentication has a vulnerability in the OAuth authentication implementation (affecting only Keycloak with a specific config). Wasp currently lowercases OAuth user IDs before storing / fetching them. This behavior violates OAuth and OpenID Connect specifications and can result in user impersonation, account collisions, and privilege escalation. In practice, out of the OAuth providers that Wasp auth supports, only Keycloak is affected. Keycloak uses a lowercase UUID by default, but users can configure it to be case sensitive, making it affected. Google, GitHub, and Discord use numerical IDs, making them not affected. Users should update their Wasp version to `0.16.6` which has a fix for the problematic behavior. Users using Keycloak can work around the issue by not using a case sensitive user ID in their realm configuration.

## References
- https://wasp-lang.notion.site/PUB-Case-insensitive-OAuth-ID-vulnerability-20018a74854c8064a2bfebe4eaf5fceb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49006.json
- https://github.com/wasp-lang/wasp/security/advisories/GHSA-qvjc-6xv7-6v5f
- https://nvd.nist.gov/vuln/detail/CVE-2025-49006
- https://github.com/wasp-lang/wasp/commit/433b9b7f491c172db656fb94cc85e5bd7d614b74
