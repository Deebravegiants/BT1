# [H] generator-jhipster allows a timing attack against validateToken due to a string comparison that stops at the first character

## Summary
Severity: High
Advisory: GHSA-4gpm-r23h-gprw
CVE: CVE-2015-20110
CWE: CWE-208, CWE-307
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-10-31
Source: https://github.com/advisories/GHSA-4gpm-r23h-gprw
Type: github-advisory

## Affected
- npm: `generator-jhipster` — affected >=0 <2.23.0

## Details
JHipster generator-jhipster before 2.23.0 allows a timing attack against validateToken due to a string comparison that stops at the first character that is different. Attackers can guess tokens by brute forcing one character at a time and observing the timing. This of course drastically reduces the search space to a linear amount of guesses based on the token length times the possible characters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-20110
- https://github.com/jhipster/generator-jhipster/issues/2095
- https://github.com/jhipster/generator-jhipster/commit/79fe5626cb1bb80f9ac86cf46980748e65d2bdbc
- https://github.com/jhipster/generator-jhipster/commit/7c49ab3d45dc4921b831a2ca55fb1e2a2db1ee25
- https://github.com/jhipster/generator-jhipster
- https://github.com/jhipster/generator-jhipster/compare/v2.22.0...v2.23.0
