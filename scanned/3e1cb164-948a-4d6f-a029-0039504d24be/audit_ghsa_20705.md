# [H] node-opcua DoS vulnerability via message with memory allocation that exceeds v8's memory limit

## Summary
Severity: High
Advisory: GHSA-qpgc-xh7j-52q8
CVE: CVE-2022-25231
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-24
Source: https://github.com/advisories/GHSA-qpgc-xh7j-52q8
Type: github-advisory

## Affected
- npm: `node-opcua` — affected >=0 <2.74.0

## Details
The package node-opcua before 2.74.0 are vulnerable to Denial of Service (DoS) by sending a specifically crafted OPC UA message with a special OPC UA NodeID, when the requested memory allocation exceeds the v8’s memory limit.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25231
- https://github.com/node-opcua/node-opcua/pull/1182
- https://github.com/node-opcua/node-opcua/commit/7b5044b3f5866fbedc3efabd05e407352c07bd2f
- https://github.com/node-opcua/node-opcua
- https://security.snyk.io/vuln/SNYK-JS-NODEOPCUA-2988724
