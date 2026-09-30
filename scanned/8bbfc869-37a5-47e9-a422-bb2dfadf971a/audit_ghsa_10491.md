# [M] MetaGPT has an eval injection in metagpt/strategy/tot.py

## Summary
Severity: Medium
Advisory: GHSA-xr7v-m9px-q4qj
CVE: CVE-2026-6110
CWE: CWE-74
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-12
Source: https://github.com/advisories/GHSA-xr7v-m9px-q4qj
Type: github-advisory

## Affected
- PyPI: `metagpt` — affected >=0

## Details
A vulnerability was identified in FoundationAgents MetaGPT up to 0.8.2. This affects the function generate_thoughts of the file metagpt/strategy/tot.py of the component Tree-of-Thought Solver. The manipulation leads to code injection. It is possible to initiate the attack remotely. The exploit is publicly available and might be used. The project was informed of the problem early through an issue report but has not responded yet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6110
- https://github.com/FoundationAgents/MetaGPT/issues/1933
- https://github.com/FoundationAgents/MetaGPT/pull/1946
- https://github.com/FoundationAgents/MetaGPT
- https://vuldb.com/submit/791761
- https://vuldb.com/vuln/356970
- https://vuldb.com/vuln/356970/cti
