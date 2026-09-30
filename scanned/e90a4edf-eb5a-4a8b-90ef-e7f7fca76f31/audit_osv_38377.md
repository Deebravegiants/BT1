# [C] dbt has a Command Injection in Reusable Workflow via Unsanitized comment-body Output

## Summary
Severity: Critical
Advisory: CVE-2026-39382
Aliases: GHSA-5jxf-vmqr-5g82
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-39382
Type: osv

## Details
dbt enables data analysts and engineers to transform their data using the same practices that software engineers use to build applications. Inside the reusable workflow dbt-labs/actions/blob/main/.github/workflows/open-issue-in-repo.yml, the prep job uses peter-evans/find-comment to search for an existing comment indicating that a docs issue has already been opened. The output steps.issue_comment.outputs.comment-body is then interpolated directly into a bash if statement. Because comment-body is attacker-controlled text and is inserted into shell syntax without escaping, a malicious comment body can break out of the quoted string and inject arbitrary shell commands. This vulnerability is fixed with commit bbed8d28354e9c644c5a7df13946a3a0451f9ab9.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39382.json
- https://github.com/dbt-labs/dbt-core/security/advisories/GHSA-5jxf-vmqr-5g82
- https://nvd.nist.gov/vuln/detail/CVE-2026-39382
- https://github.com/dbt-labs/actions/commit/bbed8d28354e9c644c5a7df13946a3a0451f9ab9
