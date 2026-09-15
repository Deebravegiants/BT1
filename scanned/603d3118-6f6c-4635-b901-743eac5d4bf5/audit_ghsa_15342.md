# [H] Flowise Cors Misconfiguration in packages/server/src/index.ts

## Summary
Severity: High
Advisory: GHSA-66f2-xxgm-f6xp
CVE: CVE-2024-36421
CWE: CWE-346
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-08-05
Source: https://github.com/advisories/GHSA-66f2-xxgm-f6xp
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0

## Details
Flowise is a drag & drop user interface to build a customized large language model flow. In version 1.4.3 of Flowise, A CORS misconfiguration sets the Access-Control-Allow-Origin header to all, allowing arbitrary origins to connect to the website. In the default configuration (unauthenticated), arbitrary origins may be able to make requests to Flowise, stealing information from the user. This CORS misconfiguration may be chained with the path injection to allow an attacker attackers without access to Flowise to read arbitrary files from the Flowise server. As of time of publication, no known patches are available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-36421
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/blob/e93ce07851cdc0fcde12374f301b8070f2043687/packages/server/src/index.ts#L122
- https://securitylab.github.com/advisories/GHSL-2023-232_GHSL-2023-234_Flowise
