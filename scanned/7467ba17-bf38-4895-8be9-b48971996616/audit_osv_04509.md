# [H] Discourse has a poll authorization bypass via post_id array parameter

## Summary
Severity: High
Advisory: BIT-discourse-2026-31805
Aliases: CVE-2026-31805, GHSA-fgxm-prjv-g823
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-discourse-2026-31805
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.3.0 <2026.3.0

## Details
Discourse is an open-source discussion platform. Prior to versions 2026.3.0, 2026.2.1, and 2026.1.2, an authorization bypass in the poll plugin allowed authenticated users to vote on, remove votes from, or toggle the open/closed status of polls they did not have access to. By passing post_id as an array (e.g. post_id[]=&post_id[]=), the authorization check resolves to the accessible post while the poll lookup resolves to a different post's poll. This affects the vote, remove_vote, and toggle_status endpoints in DiscoursePoll::PollsController. Versions 2026.3.0, 2026.2.1, and 2026.1.2 contain a patch.

## References
- https://github.com/discourse/discourse/commit/1a6b3cdd8939053f485a60a6ea004a40878392c4
- https://github.com/discourse/discourse/security/advisories/GHSA-fgxm-prjv-g823
- https://nvd.nist.gov/vuln/detail/CVE-2026-31805
