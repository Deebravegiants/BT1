# [M] Possibility for anyone to add a stack with existing tasks on anyone's board in Nextcloud Deck

## Summary
Severity: Medium
Advisory: CVE-2022-29159
Aliases: GHSA-vqhf-673w-7r3j
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N)
Published: 2022-05-20
Source: https://osv.dev/vulnerability/CVE-2022-29159
Type: osv

## Details
Nextcloud Deck is a Kanban-style project & personal management tool for Nextcloud. In versions prior to 1.4.8, 1.5.6, and 1.6.1, an authenticated user can move stacks with cards from their own board to a board of another user. The Nextcloud Deck app contains a patch for this issue in versions 1.4.8, 1.5.6, and 1.6.1. There are no known currently-known workarounds available.

## References
- https://hackerone.com/reports/1450117
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/29xxx/CVE-2022-29159.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-vqhf-673w-7r3j
- https://nvd.nist.gov/vuln/detail/CVE-2022-29159
- https://github.com/nextcloud/deck/pull/3541
