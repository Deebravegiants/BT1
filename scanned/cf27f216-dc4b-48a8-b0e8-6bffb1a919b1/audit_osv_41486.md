# [M] mcp-gitlab Path Traversal via job_id Parameter

## Summary
Severity: Medium
Advisory: CVE-2026-61462
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-61462
Type: osv

## Details
mcp-gitlab contains a path traversal vulnerability in the job_id parameter of build/index.js that allows attackers to redirect GitLab API requests to arbitrary endpoints. Attackers can supply crafted job_id values like ../../../user to escape the intended path prefix and access arbitrary GitLab API resources using the operator's personal access token.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61462.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-61462
- https://www.vulncheck.com/advisories/mcp-gitlab-path-traversal-via-job-id-parameter
- https://github.com/zereight/gitlab-mcp/issues/587
- https://github.com/zereight/gitlab-mcp/commit/e2a81a047ab8750fa5bfa1763b5d85e5616f3994
- https://github.com/zereight/gitlab-mcp
