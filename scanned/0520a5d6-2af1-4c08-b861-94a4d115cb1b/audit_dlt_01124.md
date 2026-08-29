# [C] pytorch-lightning vulnerable to Arbitrary File Write via /v1/runs API endpoint

## Summary
Severity: Critical
Chain: lightning
Component: lightning
CVE: CVE-2024-5980
CWE: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal'), Unrestricted Upload of File with Dangerous Type
Published: 2024-06-27
Source: https://github.com/advisories/GHSA-mr7h-w2qc-ffc2
Type: github-advisory

## Details
A vulnerability in the /v1/runs API endpoint of lightning-ai/pytorch-lightning v2.2.4 allows attackers to exploit path traversal when extracting tar.gz files. When the LightningApp is running with the plugin_server, attackers can deploy malicious tar.gz plugins that embed arbitrary files with path traversal vulnerabilities. This can result in arbitrary files being written to any directory in the victim's local file system, potentially leading to remote code execution.
