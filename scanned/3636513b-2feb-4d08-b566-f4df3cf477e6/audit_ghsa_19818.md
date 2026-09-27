# [C] DB-GPT is vulnerable to SQL Injection attacks from unauthenticated users

## Summary
Severity: Critical
Advisory: GHSA-qccg-9m4q-xfm6
CVE: CVE-2024-10835
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-qccg-9m4q-xfm6
Type: github-advisory

## Affected
- PyPI: `dbgpt` — affected >=0 <0.7.1

## Details
In eosphoros-ai/db-gpt version v0.6.0, the web API `POST /api/v1/editor/sql/run` allows execution of arbitrary SQL queries without any access control. This vulnerability can be exploited by attackers to perform Arbitrary File Write using DuckDB SQL, enabling them to write arbitrary files to the victim's file system. This can potentially lead to Remote Code Execution (RCE).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10835
- https://github.com/eosphoros-ai/DB-GPT/pull/2650
- https://github.com/eosphoros-ai/DB-GPT
- https://github.com/eosphoros-ai/DB-GPT/releases/tag/v0.7.1
- https://huntr.com/bounties/e32fda74-ca83-431c-8de8-08274ba686c9
