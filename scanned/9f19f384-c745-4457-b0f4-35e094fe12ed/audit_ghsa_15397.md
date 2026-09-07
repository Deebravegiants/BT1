# [M] Flowise Cross-site Scripting in/api/v1/credentials/id

## Summary
Severity: Medium
Advisory: GHSA-wxm4-9f8p-gggv
CVE: CVE-2024-37146
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-05
Source: https://github.com/advisories/GHSA-wxm4-9f8p-gggv
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0

## Details
Flowise is a drag & drop user interface to build a customized large language model flow. In version 1.4.3 of Flowise, a reflected cross-site scripting vulnerability occurs in the `/api/v1/credentials/id` endpoint. If the default configuration is used (unauthenticated), an attacker may be able to craft a specially crafted URL that injects Javascript into the user sessions, allowing the attacker to steal information, create false popups, or even redirect the user to other websites without interaction. If the chatflow ID is not found, its value is reflected in the 404 page, which has type text/html. This allows an attacker to attach arbitrary scripts to the page, allowing an attacker to steal sensitive information. This XSS may be chained with the path injection to allow an attacker without direct access to Flowise to read arbitrary files from the Flowise server. As of time of publication, no known patches are available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-37146
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/blob/flowise-ui%401.4.0/packages/server/src/index.ts#L545-L545
- https://securitylab.github.com/advisories/GHSL-2023-232_GHSL-2023-234_Flowise
