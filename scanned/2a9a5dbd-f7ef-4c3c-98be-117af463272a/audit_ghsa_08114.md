# [M] mcp-maigret vulnerable to command injection

## Summary
Severity: Medium
Advisory: GHSA-2g7v-hghf-grg4
CVE: CVE-2026-2130
CWE: CWE-74, CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-02-08
Source: https://github.com/advisories/GHSA-2g7v-hghf-grg4
Type: github-advisory

## Affected
- npm: `mcp-maigret` — affected >=0 <1.0.13

## Details
A vulnerability was determined in BurtTheCoder mcp-maigret up to 1.0.12. This affects an unknown part of the file src/index.ts of the component search_username. Executing a manipulation of the argument Username can lead to command injection. The attack may be launched remotely. Upgrading to version 1.0.13 is able to mitigate this issue. This patch is called b1ae073c4b3e789ab8de36dc6ca8111ae9399e7a. Upgrading the affected component is advised.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2130
- https://github.com/BurtTheCoder/mcp-maigret/issues/9
- https://github.com/BurtTheCoder/mcp-maigret/pull/10
- https://github.com/BurtTheCoder/mcp-maigret/commit/b1ae073c4b3e789ab8de36dc6ca8111ae9399e7a
- https://github.com/BurtTheCoder/mcp-maigret
- https://github.com/BurtTheCoder/mcp-maigret/releases/tag/v1.0.13
- https://vuldb.com/?ctiid.344765
- https://vuldb.com/?id.344765
- https://vuldb.com/?submit.747171
