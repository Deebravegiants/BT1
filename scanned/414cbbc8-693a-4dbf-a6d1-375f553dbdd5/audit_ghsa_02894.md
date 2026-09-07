# [C] XSS via prototype pollution in NodeBB 

## Summary
Severity: Critical
Advisory: GHSA-wx69-rvg3-x7fc
CVE: CVE-2021-43787
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-30
Source: https://github.com/advisories/GHSA-wx69-rvg3-x7fc
Type: github-advisory

## Affected
- npm: `nodebb` — affected >=1.15.0 <1.18.5

## Details
### Impact
A prototype pollution vulnerability in the uploader module allowed a malicious user to inject arbitrary data (i.e. javascript) into the DOM, theoretically allowing for an account takeover when used in conjunction with a path traversal vulnerability disclosed at the same time as this report.

### Patches
The vulnerability has been patched as of v1.18.5.

### Workarounds
Cherry-pick commit hash 1783f918bc19568f421473824461ff2ed7755e4c to receive this patch in lieu of a full upgrade.

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@nodebb.org](mailto:security@nodebb.org)

## References
- https://github.com/NodeBB/NodeBB/security/advisories/GHSA-wx69-rvg3-x7fc
- https://nvd.nist.gov/vuln/detail/CVE-2021-43787
- https://github.com/NodeBB/NodeBB/commit/1783f918bc19568f421473824461ff2ed7755e4c
- https://blog.sonarsource.com/nodebb-remote-code-execution-with-one-shot
- https://github.com/NodeBB/NodeBB
- https://github.com/NodeBB/NodeBB/releases/tag/v1.18.5
