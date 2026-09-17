# [M] matrix-appservice-bridge doesn't verify the sub parameter of an openId token exhange, allowing unauthorized access to provisioning APIs

## Summary
Severity: Medium
Advisory: GHSA-vc7j-h8xg-fv5x
CVE: CVE-2023-38691
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2023-08-04
Source: https://github.com/advisories/GHSA-vc7j-h8xg-fv5x
Type: github-advisory

## Affected
- npm: `matrix-appservice-bridge` — affected >=4.0.0 <8.1.2
- npm: `matrix-appservice-bridge` — affected >=9.0.0 <9.0.1

## Details
### Impact

A malicious Matrix server can use a foreign user's MXID in an OpenID exchange, allowing a bad actor to impersonate users when using the provisioning API.

### Details

The library does not check that the servername part of the `sub` parameter (containing the user's *claimed* MXID) is the same as the servername we are talking to. A malicious actor could spin up a server on any given domain, respond with a `sub` parameter according to the user they want to act as and use the resulting token to perform provisioning requests.

### Workarounds

Disable the provisioning API. If the bridge does not use the provisioning API, you are not vulnerable.

## References
- https://github.com/matrix-org/matrix-appservice-bridge/security/advisories/GHSA-vc7j-h8xg-fv5x
- https://nvd.nist.gov/vuln/detail/CVE-2023-38691
- https://github.com/matrix-org/matrix-appservice-bridge/commit/4c6723a5e7beda65cdf1ae5dbb882e8beaac8552
- https://github.com/matrix-org/matrix-appservice-bridge
