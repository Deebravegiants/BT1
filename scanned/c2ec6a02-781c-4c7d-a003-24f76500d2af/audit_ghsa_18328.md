# [M] @sequa-ai/sequa-mcp has Command Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-9pw5-wx67-q964
CVE: CVE-2025-10619
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-09-17
Source: https://github.com/advisories/GHSA-9pw5-wx67-q964
Type: github-advisory

## Affected
- npm: `@sequa-ai/sequa-mcp` — affected >=0 <1.0.14

## Details
A vulnerability was detected in sequa-ai sequa-mcp up to 1.0.13. This affects the function redirectToAuthorization of the file src/helpers/node-oauth-client-provider.ts of the component OAuth Server Discovery. Performing manipulation results in os command injection. Remote exploitation of the attack is possible. The exploit is now public and may be used. Upgrading to version 1.0.14 is able to mitigate this issue. The patch is named e569815854166db5f71c2e722408f8957fb9e804. It is recommended to upgrade the affected component. The vendor explains: "We only promote that mcp server with our own URLs that have a valid response, but yes if someone would use it with a non sequa url, this is a valid attack vector. We have released a new version (1.0.14) that fixes this and validates that only URLs can be opened."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-10619
- https://github.com/sequa-ai/sequa-mcp/commit/e569815854166db5f71c2e722408f8957fb9e804
- https://github.com/advisories/GHSA-9pw5-wx67-q964
- https://github.com/sequa-ai/sequa-mcp
- https://www.npmjs.com/package/%40sequa-ai/sequa-mcp/v/1.0.14
