# [H] Prefect has an Argument Injection issue

## Summary
Severity: High
Advisory: GHSA-cw25-2p92-7f75
CVE: CVE-2026-3515
CWE: CWE-88
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-cw25-2p92-7f75
Type: github-advisory

## Affected
- PyPI: `prefect` — affected >=0

## Details
A vulnerability in the `GitHubRepository` block of the `prefect-github` integration in Prefect version 3.6.18 allows an attacker to inject arbitrary git command-line options via the `reference` field. The `reference` field is concatenated directly into a `git clone` command string without proper sanitization, and then parsed by `shlex.split()`. This enables injection of options such as `-c`, leading to potential Server-Side Request Forgery (SSRF), credential theft, or remote code execution (RCE). The vulnerability affects both the `aget_directory()` and `get_directory()` methods in `src/integrations/prefect-github/prefect_github/repository.py`. This issue does not affect the GitLab and BitBucket integrations, which use a safer list-based command construction approach.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3515
- https://github.com/PrefectHQ/prefect
- https://huntr.com/bounties/f3b048b8-7f4e-45ef-a5a7-cb841c39acde
