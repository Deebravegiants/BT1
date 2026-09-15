# [M] vantage6 node has an Improper Access Control issue

## Summary
Severity: Medium
Advisory: GHSA-x9f6-9rvm-mmrg
CVE: CVE-2026-54533
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-x9f6-9rvm-mmrg
Type: github-advisory

## Affected
- PyPI: `vantage6` — affected >=0 <5.0.0

## Details
### Impact
Malicious algorithms can potentially access other algorithms input and output files.

### Patches
Todo

### Workarounds
Verify and restrict the algorithm containers that are allowed to run on your node. See [here](https://docs.vantage6.ai/usage/running-the-node/security) on how to do this.

### References
https://docs.vantage6.ai/usage/running-the-node/security

### For more information
If you have any questions or comments about this advisory:
* Email us at [vantage6@iknl.nl](mailto:vantage6@iknl.nl)

## References
- https://github.com/vantage6/vantage6/security/advisories/GHSA-x9f6-9rvm-mmrg
- https://nvd.nist.gov/vuln/detail/CVE-2026-54533
- https://github.com/vantage6/vantage6/issues/1932
- https://docs.vantage6.ai/usage/running-the-node/security
- https://github.com/vantage6/vantage6
- https://github.com/vantage6/vantage6/blob/main/docs/release_notes.rst#500
