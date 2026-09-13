# [H] jsonata: Malicious inputs to "$toMillis" function can cause resource exhaustion

## Summary
Severity: High
Advisory: GHSA-86vw-mfpg-wwv9
CVE: CVE-2026-52746
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-86vw-mfpg-wwv9
Type: github-advisory

## Affected
- npm: `jsonata` — affected >=2.0.0 <2.2.0
- npm: `jsonata` — affected >=0 <1.8.9

## Details
### Impact
Before JSONata `2.2.0` and `1.8.9`, it is possible to craft non-matching inputs to the [$toMillis](https://docs.jsonata.org/date-time-functions#tomillis) function that cause superlinear backtracking in the ISO-8601 validation regex. This may lead to denial of service in applications that evaluate user-provided JSONata expressions.

### Patches
This issue has been addressed in JSONata version 2.2.0 or later, and 1.8.9 or later on v1, via fixes that include https://github.com/jsonata-js/jsonata/pull/782 and https://github.com/jsonata-js/jsonata/pull/793. Applications that evaluate user-provided expressions should update ASAP to prevent exploitation.

### References
https://github.com/jsonata-js/jsonata/releases/tag/v2.2.0
https://github.com/jsonata-js/jsonata/releases/tag/v1.8.9

### Credit
Thank you to Doruk Tan Öztürk for disclosing this issue.

## References
- https://github.com/jsonata-js/jsonata/security/advisories/GHSA-86vw-mfpg-wwv9
- https://nvd.nist.gov/vuln/detail/CVE-2026-52746
- https://github.com/jsonata-js/jsonata/pull/782
- https://github.com/jsonata-js/jsonata/pull/793
- https://github.com/jsonata-js/jsonata/commit/80ba95d170f74e3f20f4f36b8b77d8c85cea7686
- https://github.com/jsonata-js/jsonata/commit/d6ffc17cb16a8e53c222205bd274624e919cce0b
- https://github.com/jsonata-js/jsonata
- https://github.com/jsonata-js/jsonata/releases/tag/v1.8.9
- https://github.com/jsonata-js/jsonata/releases/tag/v2.2.0
