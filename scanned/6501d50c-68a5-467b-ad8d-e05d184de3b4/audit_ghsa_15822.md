# [M] Lord of Large Language Models (LoLLMs)  path traversal vulnerability in the api open_personality_folder endpoint

## Summary
Severity: Medium
Advisory: GHSA-6h64-g7cj-hj56
CVE: CVE-2024-6985
CWE: CWE-23
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-10-11
Source: https://github.com/advisories/GHSA-6h64-g7cj-hj56
Type: github-advisory

## Affected
- PyPI: `lollms` — affected >=0

## Details
A path traversal vulnerability exists in the api open_personality_folder endpoint of parisneo/lollms. This vulnerability allows an attacker to read any folder in the personality_folder on the victim's computer, even though sanitize_path is set. The issue arises due to improper sanitization of the personality_folder parameter, which can be exploited to traverse directories and access arbitrary files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6985
- https://github.com/parisneo/lollms/commit/28ee567a9a120967215ff19b96ab7515ce469620
- https://github.com/ParisNeo/lollms
- https://huntr.com/bounties/79c11579-47d8-4e68-8466-b47c3bf5ef6a
