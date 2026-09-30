# [M] Sensitive fields nested in embedded values are not redacted in AshPaperTrail versions

## Summary
Severity: Medium
Advisory: CVE-2026-77970
Aliases: EEF-CVE-2026-77970, GHSA-v645-6jm6-cgpj
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-30
Source: https://osv.dev/vulnerability/CVE-2026-77970
Type: osv

## Details
Cleartext Storage of Sensitive Information vulnerability in ash-project ash_paper_trail allows an attacker with read access to the generated version resource to recover sensitive values nested inside embedded resources, unions, or lists.

sensitive_attributes :redact and :ignore only act on the tracked resource's top-level attributes. maybe_redact_changes/3 and the stored-action-input path in AshPaperTrail.Resource.Changes.CreateNewVersion derive the sensitive set from the resource's own attributes and never descend into embedded, union, or list values, so a non-sensitive attribute or action argument that holds an embed with a sensitive? field (for example an accepted credentials embed carrying a token) is written to the version table in cleartext.

This issue affects ash_paper_trail: from 0.3.0 before 0.7.0.

## References
- https://cna.erlef.org/cves/CVE-2026-77970.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-77970
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77970.json
- https://github.com/ash-project/ash_paper_trail/security/advisories/GHSA-v645-6jm6-cgpj
- https://nvd.nist.gov/vuln/detail/CVE-2026-77970
- https://github.com/ash-project/ash_paper_trail/commit/0cd4acfe7f48397673d8594fb5e2cd0f1bda6e40
- https://github.com/ash-project/ash_paper_trail
