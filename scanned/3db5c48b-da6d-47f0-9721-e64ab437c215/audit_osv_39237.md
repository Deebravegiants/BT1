# [M] Outline: Slack OAuth state can link a victim Outline account to an attacker Slack identity

## Summary
Severity: Medium
Advisory: CVE-2026-44695
Aliases: GHSA-mjgw-5j7q-gv8v
CVSS: 5.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:N/A:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-44695
Type: osv

## Details
Outline is a service that allows for collaborative documentation. Prior to 1.7.1, the Slack integration callback for GET /auth/slack.post accepts an unsigned, session-independent OAuth state value. A third party who can obtain a Slack OAuth code for the same Outline Slack client can make a logged-in Outline user complete the callback and link that user's Outline account to the attacker's Slack team_id and user_id. The linked Slack identity can then use the Slack /outline search command as the victim Outline user. This vulnerability is fixed in 1.7.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44695.json
- https://github.com/outline/outline/security/advisories/GHSA-mjgw-5j7q-gv8v
- https://nvd.nist.gov/vuln/detail/CVE-2026-44695
