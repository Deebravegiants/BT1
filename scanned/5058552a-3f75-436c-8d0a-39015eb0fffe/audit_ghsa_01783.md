# [H] Improper Input Validation in is-email

## Summary
Severity: High
Advisory: GHSA-j377-2x76-558h
CVE: CVE-2021-36716
CWE: CWE-20, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-12-10
Source: https://github.com/advisories/GHSA-j377-2x76-558h
Type: github-advisory

## Affected
- npm: `is-email` — affected >=0 <1.0.1

## Details
is-email helps validate an email address. A ReDoS (regular expression denial of service) flaw was found in the Segment is-email package before 1.0.1 for Node.js. An attacker that is able to provide crafted input to the isEmail(input) function may cause an application to consume an excessive amount of CPU.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36716
- https://github.com/segmentio/is-email
- https://github.com/segmentio/is-email/releases
- https://segment.com/docs/release_notes/2021-07-13-cve-2021-36716
