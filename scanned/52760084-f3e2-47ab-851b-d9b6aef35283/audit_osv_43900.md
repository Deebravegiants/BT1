# [M] Sensitive attribute values stored in a non-sensitive public changes map in AshPaperTrail

## Summary
Severity: Medium
Advisory: CVE-2026-75847
Aliases: EEF-CVE-2026-75847, GHSA-wqjr-xmxp-j554
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-30
Source: https://osv.dev/vulnerability/CVE-2026-75847
Type: osv

## Details
Cleartext Storage of Sensitive Information vulnerability in ash-project ash_paper_trail allows an attacker with read access to the generated version resource to recover the plaintext of sensitive? attributes.

AshPaperTrail stores the values of tracked sensitive? attributes in the generated version resource's changes map, which is declared public? true and sensitive? false, so the values are returned by the version resource's default read action and printed in logs, inspect output, and error messages instead of being redacted. AshPaperTrail.Resource.Transformers.CreateVersionResource derives the changes map's sensitivity from the ignore_attributes list (the attributes excluded from changes) rather than from the tracked attributes actually stored in it, and ignore_attributes defaults to empty, so the flag is effectively always false.

This issue affects ash_paper_trail: from 0.1.1 before 0.7.0.

## References
- https://cna.erlef.org/cves/CVE-2026-75847.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-75847
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75847.json
- https://github.com/ash-project/ash_paper_trail/security/advisories/GHSA-wqjr-xmxp-j554
- https://nvd.nist.gov/vuln/detail/CVE-2026-75847
- https://github.com/ash-project/ash_paper_trail/commit/90efdb0769f83f7c5daba6a87758daebf4baf32c
- https://github.com/ash-project/ash_paper_trail
