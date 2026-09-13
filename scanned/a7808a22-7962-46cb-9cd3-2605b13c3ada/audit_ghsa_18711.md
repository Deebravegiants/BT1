# [M] MCPHub has an Improper Authorization vulnerability via its handleSseConnection function

## Summary
Severity: Medium
Advisory: GHSA-v7c4-33vf-cqqq
CVE: CVE-2025-11287
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-10-05
Source: https://github.com/advisories/GHSA-v7c4-33vf-cqqq
Type: github-advisory

## Affected
- npm: `@samanhappy/mcphub` — affected >=0

## Details
A vulnerability was identified in samanhappy MCPHub up to 0.9.10. This vulnerability affects the function handleSseConnection of the file src/services/sseService.ts. Such manipulation leads to improper authentication. The attack may be launched remotely. The exploit is publicly available and might be used. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11287
- https://github.com/August829/YU1/issues/8
- https://github.com/samanhappy/mcphub
- https://vuldb.com/?ctiid.327045
- https://vuldb.com/?id.327045
- https://vuldb.com/?submit.661170
