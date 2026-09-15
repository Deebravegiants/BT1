# [M] kotaemon Vulnerable to Path Traversal via Link Upload

## Summary
Severity: Medium
Advisory: CVE-2025-53358
Aliases: GHSA-jw4w-xcvf-jq5x
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-07-02
Source: https://osv.dev/vulnerability/CVE-2025-53358
Type: osv

## Details
kotaemon is an open-source RAG-based tool for document comprehension. From versions 0.10.6 and prior, in libs/ktem/ktem/index/file/ui.py, the index_fn method accepts both URLs and local file paths without validation. The pipeline streams these paths directly and stores them, enabling attackers to traverse directories (e.g. ../../../../../.env) and exfiltrate sensitive files. This issue has been patched via commit 37cdc28, in version 0.10.7 which has not been made public at time of publication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53358.json
- https://github.com/Cinnamon/kotaemon/security/advisories/GHSA-jw4w-xcvf-jq5x
- https://nvd.nist.gov/vuln/detail/CVE-2025-53358
- https://github.com/Cinnamon/kotaemon/commit/37cdc28ceb46e505d25221584daf1fe61e26b2cc
- https://github.com/Cinnamon/kotaemon/pull/755
