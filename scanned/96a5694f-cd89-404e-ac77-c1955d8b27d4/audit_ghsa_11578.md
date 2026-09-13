# [M] Hyperterse: Raw exposure of database statements in MCP search tool

## Summary
Severity: Medium
Advisory: GHSA-92gp-jfgx-9qpv
CVE: CVE-2026-31841
CWE: CWE-433
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-92gp-jfgx-9qpv
Type: github-advisory

## Affected
- npm: `hyperterse` — affected >=2.0.0 <2.2.0

## Details
Hyperterse allows users to specify database queries for tools to execute under the hood. As of [v2.0.0](https://github.com/hyperterse/hyperterse/releases/tag/v2.0.0), there are only two tools exposed - `search` and `execute`. 

The `search` tool allows LLMs to search for tools using natural language. While returning results, Hyperterse also returned the raw SQL queries, exposing statements which were supposed to be executed under the hood, and protected from being displayed publicly.

This issue has been fixed as of [v2.2.0](https://github.com/hyperterse/hyperterse/releases/tag/v2.2.0) and relevant tests to catch these have been added.

## References
- https://github.com/hyperterse/hyperterse/security/advisories/GHSA-92gp-jfgx-9qpv
- https://nvd.nist.gov/vuln/detail/CVE-2026-31841
- https://github.com/hyperterse/hyperterse
- https://github.com/hyperterse/hyperterse/releases/tag/v2.2.0
