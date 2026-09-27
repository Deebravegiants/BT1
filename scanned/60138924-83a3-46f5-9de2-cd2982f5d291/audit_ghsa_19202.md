# [H] node-opcua-alarm-condition prototype pollution vulnerability

## Summary
Severity: High
Advisory: GHSA-gvwq-6fmx-28xm
CVE: CVE-2024-57086
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2025-02-06
Source: https://github.com/advisories/GHSA-gvwq-6fmx-28xm
Type: github-advisory

## Affected
- npm: `node-opcua-alarm-condition` — affected >=0 <2.137.0

## Details
A prototype pollution in the function fieldsToJson of node-opcua-alarm-condition v2.134.0 allows attackers to cause a Denial of Service (DoS) via supplying a crafted payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-57086
- https://github.com/node-opcua/node-opcua/issues/1433#issuecomment-2791824350
- https://gist.github.com/tariqhawis/30acc3632cf595ca5825b7ec2b2f795a
- https://github.com/node-opcua/node-opcua
- https://github.com/node-opcua/node-opcua/blob/330db56bb62bce9fff80382daee1fac94311978d/packages/node-opcua-alarm-condition/test/test_cve_polution_attack.ts
