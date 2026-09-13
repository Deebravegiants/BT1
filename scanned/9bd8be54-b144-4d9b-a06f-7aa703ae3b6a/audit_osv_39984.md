# [M] Postiz has an unauthenticated billing-enforcement bypass via /public/modify-subscription

## Summary
Severity: Medium
Advisory: CVE-2026-48783
Aliases: GHSA-v4wr-4j8g-4hfj
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-06-16
Source: https://osv.dev/vulnerability/CVE-2026-48783
Type: osv

## Details
Postiz is an AI social media scheduling tool. Versions prior to 2.21.8 contained an unauthenticated endpoint that accepted a signed token and applied subscription-enforcement side effects to the organization referenced in that token's claims, without verifying the token's intended purpose. The endpoint, /public/modify-subscription, could not change the persisted subscription tier, but it did execute enforcement-related side effects on the caller's own organization, including adjusting team-member enablement state, disabling integrations exceeding the asserted plan's limits, and resetting the scheduled-post cron when the asserted plan was the free tier. Impact is limited to the attacker's own organization and cannot be redirected at other tenants through this endpoint. This issue has been fixed in version 2.21.8.

## References
- https://github.com/gitroomhq/postiz-app/releases/tag/v2.21.8
- https://gadvisory.org/advisories/PSA-2026-WWFR8X
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48783.json
- https://github.com/gitroomhq/postiz-app/security/advisories/GHSA-v4wr-4j8g-4hfj
- https://nvd.nist.gov/vuln/detail/CVE-2026-48783
- https://github.com/gitroomhq/postiz-app/commit/23696d2973510ae1f3f48bfa41a6bfbbf9827b05
