# [M] FoundationAgents MetaGPT vulnerable to eval injection

## Summary
Severity: Medium
Advisory: GHSA-3ghp-8r47-4gj4
CVE: CVE-2026-5971
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-3ghp-8r47-4gj4
Type: github-advisory

## Affected
- PyPI: `metagpt` — affected >=0

## Details
A flaw has been found in FoundationAgents MetaGPT up to 0.8.1. This vulnerability affects the function ActionNode.xml_fill of the file metagpt/actions/action_node.py of the component XML Handler. Executing a manipulation can lead to improper neutralization of directives in dynamically evaluated code. The attack may be launched remotely. The exploit has been published and may be used. The project was informed of the problem early through a pull request but has not reacted yet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5971
- https://github.com/FoundationAgents/MetaGPT/issues/1928
- https://github.com/FoundationAgents/MetaGPT/issues/1956
- https://github.com/FoundationAgents/MetaGPT
- https://vuldb.com/submit/791734
- https://vuldb.com/vuln/356525
- https://vuldb.com/vuln/356525/cti
