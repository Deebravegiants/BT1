# [H] Incorrect Authorization in @uppy/companion

## Summary
Severity: High
Advisory: GHSA-q24h-5rq3-63j9
CVE: CVE-2022-0528
CWE: CWE-200, CWE-863, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-04
Source: https://github.com/advisories/GHSA-q24h-5rq3-63j9
Type: github-advisory

## Affected
- npm: `@uppy/companion` — affected >=0 <3.3.1

## Details
@uppy/companion prior to version 3.3.1 is vulnerable to incorrect authorization. A user with URL upload access could enumerate internal companion server networks, send local webservers files to the destination server, and finally download them If each of these files had a guessable and regular name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0528
- https://github.com/transloadit/uppy/commit/267c34045a1e62c98406d8c31261c604a11e544a
- https://github.com/transloadit/uppy
- https://huntr.dev/bounties/8b060cc3-2420-468e-8293-b9216620175b
