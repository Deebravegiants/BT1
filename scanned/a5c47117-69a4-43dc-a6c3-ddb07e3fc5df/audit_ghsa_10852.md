# [M] Vanna has a SQL injection in the remove_training_data function

## Summary
Severity: Medium
Advisory: GHSA-6mj8-jmp2-g8q7
CVE: CVE-2026-4229
CWE: CWE-74, CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-6mj8-jmp2-g8q7
Type: github-advisory

## Affected
- PyPI: `vanna` — affected >=0

## Details
A flaw has been found in vanna-ai vanna up to 2.0.2. This impacts the function remove_training_data of the file src/vanna/legacy/google/bigquery_vector.py. This manipulation of the argument ID causes sql injection. The attack can be initiated remotely. The exploit has been published and may be used. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4229
- https://gist.github.com/YLChen-007/b4f326eaecc29b192cf93dc5d6bc0623
- https://github.com/vanna-ai/vanna
- https://vuldb.com/?ctiid.351152
- https://vuldb.com/?id.351152
- https://vuldb.com/?submit.771214
