# [C] smolagents has Sandbox Escape Vulnerability in the local_python_executor.py Module

## Summary
Severity: Critical
Advisory: GHSA-6v92-r5mx-h5fx
CVE: CVE-2025-5120
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:L (CVSS_V3)
Published: 2025-07-27
Source: https://github.com/advisories/GHSA-6v92-r5mx-h5fx
Type: github-advisory

## Affected
- PyPI: `smolagents` — affected >=0 <1.17.0

## Details
A sandbox escape vulnerability was identified in huggingface/smolagents version 1.14.0, allowing attackers to bypass the restricted execution environment and achieve remote code execution (RCE). The vulnerability stems from the local_python_executor.py module, which inadequately restricts Python code execution despite employing static and dynamic checks. Attackers can exploit whitelisted modules and functions to execute arbitrary code, compromising the host system. This flaw undermines the core security boundary intended to isolate untrusted code, posing risks such as unauthorized code execution, data leakage, and potential integration-level compromise. The issue is resolved in version 1.17.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-5120
- https://github.com/huggingface/smolagents/commit/33a942e62b6fbf6a35d41f1c735bda2d64c163d0
- https://github.com/huggingface/smolagents
- https://huntr.com/bounties/63ab1cfe-b573-4cf5-a7d3-fb6c957e34b0
