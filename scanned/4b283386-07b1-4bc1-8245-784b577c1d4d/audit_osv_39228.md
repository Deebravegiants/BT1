# [H] LibreChat: Shared-agent editor can globally delete owner's file records — breaks owner's other private agents

## Summary
Severity: High
Advisory: CVE-2026-44654
Aliases: GHSA-f8jg-v856-mf6q
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-06-02
Source: https://osv.dev/vulnerability/CVE-2026-44654
Type: osv

## Details
LibreChat is an enhanced ChatGPT clone that supports multiple AI providers. In versions up to and including 0.8.3, a shared-agent editor can delete file records through `DELETE /api/files` that the owner has reused across multiple agents. The deletion removes the file globally — not just from the shared agent — breaking the owner's other private agents that reference the same `file_id`. The private agent retains a stale `file_id` reference that no longer resolves. A shared-agent editor can destroy files that the owner uses across multiple agents. The owner's private agents — which the attacker has no access to — break silently with stale `file_id` references. This is a cross-agent integrity violation: editing access to one agent should not affect another. Version 0.8.4 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44654.json
- https://github.com/danny-avila/LibreChat/security/advisories/GHSA-f8jg-v856-mf6q
- https://nvd.nist.gov/vuln/detail/CVE-2026-44654
