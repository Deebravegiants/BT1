# [M] AiondaDotCom mcp-ssh command injection vulnerability in SSH operations

## Summary
Severity: Medium
Advisory: GHSA-694p-3fxc-m92h
CVE: CVE-2025-9654
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-08-29
Source: https://github.com/advisories/GHSA-694p-3fxc-m92h
Type: github-advisory

## Affected
- npm: `@aiondadotcom/mcp-ssh` — affected >=0 <1.1.0

## Details
A security flaw has been discovered in AiondaDotCom mcp-ssh up to 1.0.3. Affected by this issue is some unknown functionality of the file server-simple.mjs. Performing manipulation results in command injection. The attack can be initiated remotely. Upgrading to version 1.0.4 and 1.1.0 can resolve this issue. The patch is named cd2566a948b696501abfa6c6b03462cac5fb43d8. It is advisable to upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-9654
- https://github.com/AiondaDotCom/mcp-ssh/commit/5b9b9c5b28d3f2672f356a790154ed68e17ef453
- https://github.com/AiondaDotCom/mcp-ssh/commit/cd2566a948b696501abfa6c6b03462cac5fb43d8
- https://github.com/AiondaDotCom/mcp-ssh
- https://vuldb.com/?ctiid.321862
- https://vuldb.com/?id.321862
- https://vuldb.com/?submit.637028
