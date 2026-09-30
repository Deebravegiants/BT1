# [M] api-lab-mcp vulnerable to SSRF

## Summary
Severity: Medium
Advisory: GHSA-crh9-3gjh-m6gc
CVE: CVE-2026-5832
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-crh9-3gjh-m6gc
Type: github-advisory

## Affected
- npm: `api-lab-mcp` — affected >=0

## Details
A weakness has been identified in atototo api-lab-mcp up to 0.2.1. This affects the function analyze_api_spec/generate_test_scenarios/test_http_endpoint of the file src/mcp/http-server.ts of the component HTTP Interface. This manipulation of the argument source/url causes server-side request forgery. The attack is possible to be carried out remotely. The exploit has been made available to the public and could be used for attacks. The project was informed of the problem early through an issue report but has not responded yet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5832
- https://github.com/BruceJqs/public_exp/issues/6
- https://github.com/atototo/api-lab-mcp/issues/4
- https://github.com/atototo/api-lab-mcp
- https://vuldb.com/submit/789765
- https://vuldb.com/vuln/356288
- https://vuldb.com/vuln/356288/cti
