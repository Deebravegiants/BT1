# [M] Denial of service in fastify

## Summary
Severity: Medium
Advisory: GHSA-xw5p-hw6r-2j98
CVE: CVE-2020-8192
CWE: CWE-400
Ecosystem: npm
Published: 2020-08-05
Source: https://github.com/advisories/GHSA-xw5p-hw6r-2j98
Type: github-advisory

## Affected
- npm: `fastify` — affected >=0 <2.15.1

## Details
A denial of service vulnerability exists in Fastify v2.14.1 and v3.0.0-rc.4 that allows a malicious user to trigger resource exhaustion (when the allErrors option is used) with specially crafted schemas.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8192
- https://github.com/fastify/fastify/commit/74c3157ca90c3ffed9e4434f63c2017471ec970e
- https://hackerone.com/reports/903521
