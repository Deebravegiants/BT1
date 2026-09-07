# [H] LoLLMS vulnerable to Expected Behavior Violation

## Summary
Severity: High
Advisory: GHSA-8mrm-r7h3-c3hj
CVE: CVE-2024-6281
CWE: CWE-22, CWE-440
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2024-07-20
Source: https://github.com/advisories/GHSA-8mrm-r7h3-c3hj
Type: github-advisory

## Affected
- PyPI: `lollms` — affected >=0 <9.5.1

## Details
A path traversal vulnerability exists in the `apply_settings` function of parisneo/lollms versions prior to 9.5.1. The `sanitize_path` function does not adequately secure the `discussion_db_name` parameter, allowing attackers to manipulate the path and potentially write to important system folders.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6281
- https://github.com/parisneo/lollms/commit/26a3ff35acf152b49e1087d5698ad4864c7b6092
- https://github.com/parisneo/lollms
- https://huntr.com/bounties/0a62f2fb-4e62-4128-9dc4-e8f1d959ac61
