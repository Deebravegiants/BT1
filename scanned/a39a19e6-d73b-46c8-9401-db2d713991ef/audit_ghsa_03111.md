# [M] Uncontrolled Resource Consumption in fastify-multipart

## Summary
Severity: Medium
Advisory: GHSA-p9f8-gqjf-m75j
CVE: CVE-2020-8136
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-p9f8-gqjf-m75j
Type: github-advisory

## Affected
- npm: `fastify-multipart` — affected >=0 <1.0.5

## Details
Prototype pollution vulnerability in `fastify-multipart` < 1.0.5 allows an attacker to crash fastify applications parsing multipart requests by sending a specially crafted request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8136
- https://hackerone.com/reports/804772
