# [H] node-opcua DoS when bypassing limitations for excessive memory consumption

## Summary
Severity: High
Advisory: GHSA-vh4f-fgpp-x8x2
CVE: CVE-2022-24375
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-25
Source: https://github.com/advisories/GHSA-vh4f-fgpp-x8x2
Type: github-advisory

## Affected
- npm: `node-opcua` — affected >=0 <2.74.0

## Details
The package node-opcua before 2.74.0 are vulnerable to Denial of Service (DoS) when bypassing the limitations for excessive memory consumption by sending multiple `CloseSession` requests with the `deleteSubscription` parameter equal to `False`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24375
- https://github.com/node-opcua/node-opcua/pull/1182
- https://github.com/node-opcua/node-opcua/commit/3fd46ec156e7718a506be41f3916310b6bdd0407
- https://github.com/node-opcua/node-opcua/commit/7b5044b3f5866fbedc3efabd05e407352c07bd2f
- https://github.com/node-opcua/node-opcua
- https://security.snyk.io/vuln/SNYK-JS-NODEOPCUA-2988725
