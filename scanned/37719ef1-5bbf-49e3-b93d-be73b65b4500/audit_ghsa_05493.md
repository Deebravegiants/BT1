# [M] Pterodactyl improperly locks resources allowing raced queries to create more resources than alloted

## Summary
Severity: Medium
Advisory: GHSA-jw2v-cq5x-q68g
CVE: CVE-2025-69198
CWE: CWE-362, CWE-400, CWE-413, CWE-667
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-20
Source: https://github.com/advisories/GHSA-jw2v-cq5x-q68g
Type: github-advisory

## Affected
- Packagist: `pterodactyl/panel` — affected >=0 <1.12.0

## Details
### Summary
Pterodactyl implements rate limits that are applied to the total number of resources (e.g. databases, port allocations, or backups) that can exist for an individual server. These resource limits are applied on a per-server basis, and validated during the request cycle.

However, it is possible for a malicious user to send a massive volume of requests at the same time that would create more resources than the server is allotted. This is because the validation occurs early in the request cycle and does not lock the target resource while it is processing. As a result sending a large volume of requests at the same time would lead all of those requests to validate as not using any of the target resources, and then all creating the resources at the same time.

As a result a server would be able to create more databases, allocations, or backups than configured.

### Impact
A malicious user is able to deny resources to other users on the system, and may be able to excessively consume the limited allocations for a node, or fill up backup space faster than is allowed by the system.

## References
- https://github.com/pterodactyl/panel/security/advisories/GHSA-jw2v-cq5x-q68g
- https://nvd.nist.gov/vuln/detail/CVE-2025-69198
- https://github.com/pterodactyl/panel/commit/09caa0d4995bd924b53b9a9e9b4883ac27bd5607
- https://github.com/pterodactyl/panel
