# [H] Denial of service in http-proxy-middleware

## Summary
Severity: High
Advisory: GHSA-c7qv-q95q-8v27
CVE: CVE-2024-21536
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-10-19
Source: https://github.com/advisories/GHSA-c7qv-q95q-8v27
Type: github-advisory

## Affected
- npm: `http-proxy-middleware` — affected >=0 <2.0.7
- npm: `http-proxy-middleware` — affected >=3.0.0 <3.0.3

## Details
Versions of the package http-proxy-middleware before 2.0.7, from 3.0.0 and before 3.0.3 are vulnerable to Denial of Service (DoS) due to an UnhandledPromiseRejection error thrown by micromatch. An attacker could kill the Node.js process and crash the server by making requests to certain paths.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21536
- https://github.com/chimurai/http-proxy-middleware/commit/0b4274e8cc9e9a2c5a06f35fbf456ccfcebc55a5
- https://github.com/chimurai/http-proxy-middleware/commit/788b21e4aff38332d6319557d4a5b1b13b1f9a22
- https://gist.github.com/mhassan1/28be67266d82a53708ed59ce5dc3c94a
- https://github.com/chimurai/http-proxy-middleware
- https://security.snyk.io/vuln/SNYK-JS-HTTPPROXYMIDDLEWARE-8229906
