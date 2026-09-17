# [M] SSRF Vulnerabilities in significant-gravitas/autogpt

## Summary
Severity: Medium
Advisory: CVE-2024-10457
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-10457
Type: osv

## Details
Multiple Server-Side Request Forgery (SSRF) vulnerabilities were identified in the significant-gravitas/autogpt repository, specifically in the GitHub Integration and Web Search blocks. These vulnerabilities affect version agpt-platform-beta-v0.1.1. The issues arise when block inputs are controlled by untrusted sources, leading to potential credential leakage, internal network scanning, and unauthorized access to internal services, APIs, or data stores. The affected blocks include GithubListPullRequestsBlock, GithubReadPullRequestBlock, GithubAssignPRReviewerBlock, GithubListPRReviewersBlock, GithubUnassignPRReviewerBlock, GithubCommentBlock, GithubMakeIssueBlock, GithubReadIssueBlock, GithubListIssuesBlock, GithubAddLabelBlock, GithubRemoveLabelBlock, GithubListBranchesBlock, and ExtractWebsiteContentBlock.

## References
- https://huntr.com/bounties/1d91e1e1-7d45-4bda-bc27-bfe9052fd975
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10457.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10457
- https://github.com/significant-gravitas/autogpt/commit/bcaf3241dadfc1fca024e91fb8f2e3004105a172
