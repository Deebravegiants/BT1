# [C] API token verification can be bypassed in NodeBB 

## Summary
Severity: Critical
Advisory: GHSA-hf2m-j98r-4fqw
CVE: CVE-2021-43786
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-30
Source: https://github.com/advisories/GHSA-hf2m-j98r-4fqw
Type: github-advisory

## Affected
- npm: `nodebb` — affected >=1.15.0 <1.18.5

## Details
### Impact
Incorrect logic present in the token verification step unintentionally allowed master token access to the API.

### Patches
The vulnerability has been patch as of v1.18.5.

### Workarounds
Cherry-pick commit hash 04dab1d550cdebf4c1567bca9a51f8b9ca48a500 to receive this patch in lieu of a full upgrade.

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@nodebb.org](mailto:security@nodebb.org)

## References
- https://github.com/NodeBB/NodeBB/security/advisories/GHSA-hf2m-j98r-4fqw
- https://nvd.nist.gov/vuln/detail/CVE-2021-43786
- https://github.com/NodeBB/NodeBB/commit/04dab1d550cdebf4c1567bca9a51f8b9ca48a500
- https://blog.sonarsource.com/nodebb-remote-code-execution-with-one-shot
- https://github.com/NodeBB/NodeBB
- https://github.com/NodeBB/NodeBB/releases/tag/v1.18.5
