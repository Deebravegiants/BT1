# [H] Command injection in docker-tester

## Summary
Severity: High
Advisory: GHSA-rj88-4777-828h
CVE: CVE-2021-34079
CWE: CWE-74
Ecosystem: npm
Published: 2022-06-03
Source: https://github.com/advisories/GHSA-rj88-4777-828h
Type: github-advisory

## Affected
- npm: `docker-tester` — affected >=0

## Details
OS Command injection vulnerability in Mintzo Docker-Tester through 1.2.1 allows attackers to execute arbitrary commands via shell metacharacters in the 'ports' entry of a crafted docker-compose.yml file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-34079
- https://advisory.checkmarx.net/advisory/CX-2021-4786
- https://github.com/mintzo/docker-testing
- https://www.npmjs.com/package/docker-tester
