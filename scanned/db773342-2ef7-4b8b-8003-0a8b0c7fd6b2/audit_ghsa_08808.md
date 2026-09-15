# [M] sublinear-time-solver has a Path Traversal Issue

## Summary
Severity: Medium
Advisory: GHSA-gc2j-wpjv-jhrw
CVE: CVE-2026-7645
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-05-02
Source: https://github.com/advisories/GHSA-gc2j-wpjv-jhrw
Type: github-advisory

## Affected
- npm: `sublinear-time-solver` — affected >=0

## Details
A vulnerability was found in ruvnet sublinear-time-solver 1.5.0. Affected by this vulnerability is the function export_state of the file src/consciousness-explorer/mcp/server.js of the component MCP Interface. The manipulation results in path traversal. The attack can be executed remotely. The exploit has been made public and could be used. The project was informed of the problem early through an issue report but has not responded yet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7645
- https://github.com/ruvnet/sublinear-time-solver/issues/19
- https://github.com/ruvnet/sublinear-time-solver
- https://vuldb.com/submit/806895
- https://vuldb.com/vuln/360757
- https://vuldb.com/vuln/360757/cti
