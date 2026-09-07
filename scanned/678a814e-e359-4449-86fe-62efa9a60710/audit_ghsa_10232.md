# [M] FoundationAgents MetaGPT vulnerable to os command injection via the Terminal.run_command

## Summary
Severity: Medium
Advisory: GHSA-wp29-qmvj-frvp
CVE: CVE-2026-5972
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-wp29-qmvj-frvp
Type: github-advisory

## Affected
- PyPI: `metagpt` — affected >=0 <0.8.2

## Details
A vulnerability has been found in FoundationAgents MetaGPT up to 0.8.1. This issue affects the function Terminal.run_command in the library metagpt/tools/libs/terminal.py. The manipulation leads to os command injection. Remote exploitation of the attack is possible. The exploit has been disclosed to the public and may be used. The identifier of the patch is d04ffc8dc67903e8b327f78ec121df5e190ffc7b. Applying a patch is the recommended action to fix this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5972
- https://github.com/FoundationAgents/MetaGPT/issues/1929
- https://github.com/paipeline/MetaGPT/commit/d04ffc8dc67903e8b327f78ec121df5e190ffc7b
- https://github.com/FoundationAgents/MetaGPT
- https://vuldb.com/submit/791745
- https://vuldb.com/vuln/356526
- https://vuldb.com/vuln/356526/cti
