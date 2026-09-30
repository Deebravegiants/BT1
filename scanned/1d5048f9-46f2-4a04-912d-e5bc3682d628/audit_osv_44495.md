# [M] Ash relationship parent(...) filter degrades to an IS NULL match when the parent field is unresolved, leaking scoped records

## Summary
Severity: Medium
Advisory: CVE-2026-82749
Aliases: EEF-CVE-2026-82749, GHSA-j8fx-ff37-4j9c
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-82749
Type: osv

## Details
Incorrect Authorization vulnerability in ash-project ash widens a relationship's parent(...) scoping filter to match unintended records when the referenced parent field cannot be resolved.

Loading a relationship whose filter references parent(...) resolves that expression against the parent record. resolve_parent_in_filter/3 (lib/ash/actions/read/relationships.ex) resolved an unresolvable parent reference (for example when the referenced field was not selected on the source query) to nil rather than failing. A scoping predicate such as org_id == parent(org_id) then becomes an IS NULL match, and a guard like is_nil(parent(org_id)) or org_id == parent(org_id) activates its unrestricted branch, so the relationship returns records the scope was meant to exclude. The fix fails the read with an error when a parent(...) reference cannot be resolved, instead of defaulting to nil.

This issue affects ash: from 3.13.2 before 3.32.2.

## References
- https://cna.erlef.org/cves/CVE-2026-82749.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-82749
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82749.json
- https://github.com/ash-project/ash/security/advisories/GHSA-j8fx-ff37-4j9c
- https://nvd.nist.gov/vuln/detail/CVE-2026-82749
- https://github.com/ash-project/ash/commit/e52dad2c39a35f6f043f7324d26e4f4e2551dfd2
- https://github.com/ash-project/ash
