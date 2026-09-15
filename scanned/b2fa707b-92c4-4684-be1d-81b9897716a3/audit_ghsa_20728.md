# [H] Uncontrolled Resource Consumption in node-opcua

## Summary
Severity: High
Advisory: GHSA-4hr4-pjjh-2q2w
CVE: CVE-2022-21208
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-24
Source: https://github.com/advisories/GHSA-4hr4-pjjh-2q2w
Type: github-advisory

## Affected
- npm: `node-opcua` — affected >=0 <2.74.0

## Details
The package node-opcua before 2.74.0 are vulnerable to Denial of Service (DoS) due to a missing limitation on the number of received chunks - per single session or in total for all concurrent sessions. An attacker can exploit this vulnerability by sending an unlimited number of huge chunks (e.g. 2GB each) without sending the Final closing chunk.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21208
- https://github.com/node-opcua/node-opcua/pull/1149
- https://github.com/node-opcua/node-opcua/commit/33ca3bab4ab781392a2f8d8f5a14de9a0aa0e410
- https://github.com/node-opcua/node-opcua/commit/dbcb5d5191118c22ee9c89332a94b94e6553d76b
- https://github.com/node-opcua/node-opcua
- https://security.snyk.io/vuln/SNYK-JS-NODEOPCUA-2988723
