# [M] Zulip: Message edit history visible in "moves only" policy through /api/v1/messages/{id}/history

## Summary
Severity: Medium
Advisory: CVE-2026-40300
Aliases: GHSA-jp8f-mvv6-89cr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-40300
Type: osv

## Details
Zulip is an open-source team collaboration tool. Prior to 12.0, With message_edit_history_visibility_policy set to "moves", /api/v1/messages/{id}/history still returns historical content values, allowing low-privilege users to recover text that was edited away from other users' messages. This vulnerability is fixed in 12.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40300.json
- https://github.com/zulip/zulip/security/advisories/GHSA-jp8f-mvv6-89cr
- https://nvd.nist.gov/vuln/detail/CVE-2026-40300
