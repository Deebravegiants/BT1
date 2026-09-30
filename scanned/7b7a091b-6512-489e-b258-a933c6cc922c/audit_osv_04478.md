# [M] Discourse Has Denial of Service (DoS) Vulnerability in Drafts Creation Endpoint

## Summary
Severity: Medium
Advisory: BIT-discourse-2025-68934
Aliases: CVE-2025-68934, GHSA-vwjh-vrx9-9849
Ecosystem: Bitnami
Published: 2026-02-02
Source: https://osv.dev/vulnerability/BIT-discourse-2025-68934
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2025.12.0 <2026.1.0

## Details
Discourse is an open source discussion platform. In versions prior to 3.5.4, 2025.11.2, 2025.12.1, and 2026.1.0, authenticated users can submit crafted payloads to /drafts.json that cause O(n^2) processing in Base62.decode, tying up workers for 35-60 seconds per request. This affects all users as the shared worker pool becomes exhausted. This issue is patched in versions 3.5.4, 2025.11.2, 2025.12.1, and 2026.1.0. Lowering the max_draft_length site setting reduces attack surface but does not fully mitigate the issue, as payloads under the limit can still trigger the slow code path.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-vwjh-vrx9-9849
- https://nvd.nist.gov/vuln/detail/CVE-2025-68934
