# [M] MetaGPT has an Injection issue

## Summary
Severity: Medium
Advisory: GHSA-g977-h85w-h2xj
CVE: CVE-2026-5970
CWE: CWE-74
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-g977-h85w-h2xj
Type: github-advisory

## Affected
- PyPI: `metagpt` — affected >=0

## Details
A vulnerability was detected in FoundationAgents MetaGPT up to 0.8.1. This affects the function check_solution of the component HumanEvalBenchmark/MBPPBenchmark. Performing a manipulation results in code injection. The attack may be initiated remotely. The exploit is now public and may be used. The project was informed of the problem early through a pull request but has not reacted yet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5970
- https://github.com/FoundationAgents/MetaGPT/issues/1942
- https://github.com/FoundationAgents/MetaGPT/pull/1988
- https://github.com/FoundationAgents/MetaGPT
- https://vuldb.com/submit/791693
- https://vuldb.com/vuln/356524
- https://vuldb.com/vuln/356524/cti
