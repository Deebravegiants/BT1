# [M] FoundationAgents MetaGPT vulnerable to OS Command Injection in metagpt/utils/common.py

## Summary
Severity: Medium
Advisory: GHSA-qw5f-qpq5-ppfg
CVE: CVE-2026-5973
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-qw5f-qpq5-ppfg
Type: github-advisory

## Affected
- PyPI: `metagpt` — affected >=0

## Details
A vulnerability was found in FoundationAgents MetaGPT up to 0.8.1. Impacted is the function get_mime_type of the file metagpt/utils/common.py. The manipulation results in os command injection. The attack can be executed remotely. The exploit has been made public and could be used. The project was informed of the problem early through a pull request but has not reacted yet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5973
- https://github.com/FoundationAgents/MetaGPT/issues/1930
- https://github.com/FoundationAgents/MetaGPT/pull/1983
- https://github.com/FoundationAgents/MetaGPT
- https://vuldb.com/submit/791755
- https://vuldb.com/vuln/356527
- https://vuldb.com/vuln/356527/cti
