# [C] OpenLIT Vulnerable to Remote Code Execution and Secret Exposure via Misuse of `pull_request_target` in GitHub Actions Workflows

## Summary
Severity: Critical
Advisory: CVE-2026-27941
Aliases: GHSA-9jgv-x8cq-296q, PYSEC-2026-2246
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-02-26
Source: https://osv.dev/vulnerability/CVE-2026-27941
Type: osv

## Details
OpenLIT is an open source platform for AI engineering. Prior to version 1.37.1, several GitHub Actions workflows in OpenLIT's GitHub repository use the `pull_request_target` event while checking out and executing untrusted code from forked pull requests. These workflows run with the security context of the base repository, including a write-privileged `GITHUB_TOKEN` and numerous sensitive secrets (API keys, database/vector store tokens, and a Google Cloud service account key). Version 1.37.1 contains a fix.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27941.json
- https://github.com/openlit/openlit/security/advisories/GHSA-9jgv-x8cq-296q
- https://nvd.nist.gov/vuln/detail/CVE-2026-27941
- https://github.com/openlit/openlit/commit/4a62039a1659d6cbb8913172693f587b5fc2546c
