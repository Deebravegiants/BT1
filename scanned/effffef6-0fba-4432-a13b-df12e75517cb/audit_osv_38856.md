# [M] Insufficient authorization in shared channel membership sync grants team-level access instead of channel-level access

## Summary
Severity: Medium
Advisory: CVE-2026-4274
Aliases: GHSA-g7fp-cqj5-x8hf, GO-2026-5393
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-4274
Type: osv

## Details
Mattermost versions 11.2.x <= 11.2.2, 10.11.x <= 10.11.10, 11.4.x <= 11.4.0, 11.3.x <= 11.3.1 fail to restrict team-level access when processing membership sync from a remote cluster, which allows a malicious remote cluster to grant a user access to an entire private team instead of only the shared channel via sending crafted membership sync messages that trigger team membership assignment. Mattermost Advisory ID: MMSA-2026-00574

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/4xxx/CVE-2026-4274.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-4274
