# [M] Matrix SDK for React's URL preview setting for a room is controllable by the homeserver

## Summary
Severity: Medium
Advisory: GHSA-f83w-wqhc-cfp4
CVE: CVE-2024-42347
CWE: CWE-359
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2024-08-06
Source: https://github.com/advisories/GHSA-f83w-wqhc-cfp4
Type: github-advisory

## Affected
- npm: `matrix-react-sdk` — affected >=0 <3.105.1

## Details
### Impact
A malicious homeserver could manipulate a user's account data to cause the client to enable URL previews in end-to-end encrypted rooms, in which case any URLs in encrypted messages would be sent to the server.

Even if the CVSS score would be 4.1 ([AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:N/A:N](https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator?vector=AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:N/A:N&version=3.1)) the maintainer classifies this as High severity issue.

### Patches
This was patched in matrix-react-sdk 3.105.1.

### Workarounds
Deployments that trust their homeservers, as well as closed federations of trusted servers, are not affected.

### References
N/A.

## References
- https://github.com/matrix-org/matrix-react-sdk/security/advisories/GHSA-f83w-wqhc-cfp4
- https://nvd.nist.gov/vuln/detail/CVE-2024-42347
- https://github.com/matrix-org/matrix-react-sdk
- https://github.com/matrix-org/matrix-react-sdk/releases/tag/v3.105.1
