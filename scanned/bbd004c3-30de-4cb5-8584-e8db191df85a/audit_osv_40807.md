# [M] MaaAssistantArknights: PR-title expression injection in release-preparation.yml

## Summary
Severity: Medium
Advisory: CVE-2026-55576
Aliases: GHSA-pqx2-5g66-f5w8
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-55576
Type: osv

## Details
MaaAssistantArknights is a one-click tool for daily Arknights tasks. In the current dev-v2 workflow, .github/workflows/release-preparation.yml inlined attacker-controlled github.event.pull_request.title into a run: shell command during the pull_request opened, reopened, and ready_for_review events, so a non-draft fork PR whose title starts with Release v could execute shell commands on the ubuntu-latest runner during the generate-changelog job. This vulnerability is fixed by commit cafc3946059e6337d2089d4fec8b6885ba17c332.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55576.json
- https://github.com/MaaAssistantArknights/MaaAssistantArknights/security/advisories/GHSA-pqx2-5g66-f5w8
- https://nvd.nist.gov/vuln/detail/CVE-2026-55576
- https://github.com/MaaAssistantArknights/MaaAssistantArknights/commit/cafc3946059e6337d2089d4fec8b6885ba17c332
