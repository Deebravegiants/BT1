# [C] DB-GPT Arbitrary File Write vulnerability

## Summary
Severity: Critical
Advisory: GHSA-7gj6-22m4-qfhx
CVE: CVE-2024-10901
CWE: CWE-434, CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-7gj6-22m4-qfhx
Type: github-advisory

## Affected
- PyPI: `dbgpt` — affected >=0

## Details
In eosphoros-ai/db-gpt version v0.6.3 and earlier, the web API `POST /api/v1/editor/chart/run` allows execution of arbitrary SQL queries without any access control. This vulnerability can be exploited by attackers to perform Arbitrary File Write, enabling them to write arbitrary files to the victim's file system. This can potentially lead to Remote Code Execution (RCE) by writing malicious files such as `__init__.py` in the Python's `/site-packages/` directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10901
- https://github.com/eosphoros-ai/DB-GPT/pull/2269
- https://github.com/eosphoros-ai/DB-GPT/commit/295cdb8723663d5b0954d5d1dfb4f02b7223b8ff
- https://github.com/eosphoros-ai/DB-GPT
- https://huntr.com/bounties/db2c1d59-6e3a-4553-a1f6-94c8df162a18
