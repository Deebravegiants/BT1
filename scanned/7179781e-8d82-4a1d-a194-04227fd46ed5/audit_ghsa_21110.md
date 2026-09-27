# [M] Passport vulnerable to session regeneration when a users logs in or out

## Summary
Severity: Medium
Advisory: GHSA-v923-w3x8-wh69
CVE: CVE-2022-25896
CWE: CWE-384
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2022-07-02
Source: https://github.com/advisories/GHSA-v923-w3x8-wh69
Type: github-advisory

## Affected
- npm: `passport` — affected >=0 <0.6.0

## Details
This affects the package passport before 0.6.0. When a user logs in or logs out, the session is regenerated instead of being closed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25896
- https://github.com/jaredhanson/passport/pull/900
- https://github.com/jaredhanson/passport/commit/7e9b9cf4d7be02428e963fc729496a45baeea608
- https://github.com/jaredhanson/passport
- https://snyk.io/vuln/SNYK-JS-PASSPORT-2840631
