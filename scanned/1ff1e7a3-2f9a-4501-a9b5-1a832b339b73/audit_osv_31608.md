# [M] Wazuh GitHub Actions Workflow Exposure of Sensitive Credentials

## Summary
Severity: Medium
Advisory: CVE-2025-15617
Aliases: GHSA-6xqr-4q5g-xc7x
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2025-15617
Type: osv

## Details
Wazuh version 4.12.0 contains an exposure vulnerability in GitHub Actions workflow artifacts that allows attackers to extract the GITHUB_TOKEN from uploaded artifacts. Attackers can use the exposed token within a limited time window to perform unauthorized actions such as pushing malicious commits or altering release tags.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/15xxx/CVE-2025-15617.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-6xqr-4q5g-xc7x
- https://nvd.nist.gov/vuln/detail/CVE-2025-15617
- https://www.vulncheck.com/advisories/exposure-of-the-github-token-in-wazuh-workflow-run-artifact
