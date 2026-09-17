# [M] Discourse: Category queue reviewers can read raw incoming emails from queued posts

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-44780
Aliases: CVE-2026-44780, GHSA-h2jr-whpx-6w63
Ecosystem: Bitnami
Published: 2026-06-16
Source: https://osv.dev/vulnerability/BIT-discourse-2026-44780
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.4.0 <2026.4.1

## Details
Discourse is an open-source discussion platform. From versions 2026.1.0 to before 2026.1.4, 2026.3.0 to before 2026.3.1, and 2026.4.0 to before 2026.4.1, ReviewableQueuedPostSerializer unconditionally included payload["raw_email"] for posts that arrived via incoming email. Category moderation group members reaching the review queue could therefore read the full inbound email source (headers, sender trace, MUA, body) without being in view_raw_email_allowed_groups — the trust boundary that gates the dedicated raw-email endpoint. This issue has been patched in versions 2026.1.4, 2026.3.1, 2026.4.1, and 2026.5.0.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-h2jr-whpx-6w63
- https://nvd.nist.gov/vuln/detail/CVE-2026-44780
