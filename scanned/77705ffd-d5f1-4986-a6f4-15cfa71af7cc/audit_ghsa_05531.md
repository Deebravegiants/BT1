# [M] n8n: Webhook Node IP Whitelist Bypass via Partial String Matching

## Summary
Severity: Medium
Advisory: GHSA-w96v-gf22-crwp
CVE: CVE-2025-68949
CWE: CWE-134, CWE-183, CWE-284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-w96v-gf22-crwp
Type: github-advisory

## Affected
- npm: `n8n` — affected >=1.36.0 <2.2.0

## Details
## Impact
The Webhook node’s IP whitelist validation performed partial string matching instead of exact IP comparison. As a result, an incoming request could be accepted if the source IP address merely contained the configured whitelist entry as a substring.

This issue affected instances where workflow editors relied on IP-based access controls to restrict webhook access. Both IPv4 and IPv6 addresses were impacted. An attacker with a non-whitelisted IP could bypass restrictions if their IP shared a partial prefix with a trusted address, undermining the intended security boundary.

## Patches
This issue has been patched in version 2.2.0.

Users are advised to upgrade to v2.2.0 or later, where IP whitelist validation uses strict IP comparison logic rather than partial string matching.

## Workarounds
Users unable to upgrade immediately should avoid relying solely on IP whitelisting for webhook security. Recommended mitigations include:
- Adding authentication mechanisms such as shared secrets, HMAC signatures, or API keys.
- Avoiding short or prefix-based whitelist entries.
- Enforcing IP filtering at the network layer (for example, via reverse proxies or firewalls).

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-w96v-gf22-crwp
- https://nvd.nist.gov/vuln/detail/CVE-2025-68949
- https://github.com/n8n-io/n8n/issues/23399
- https://github.com/n8n-io/n8n/pull/23399
- https://github.com/n8n-io/n8n/commit/11f8597d4ad69ea3b58941573997fdbc4de1fec5
- https://github.com/n8n-io/n8n
