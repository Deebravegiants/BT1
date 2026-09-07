# [M] brace-expansion: Large numeric range defeats documented `max` DoS protection

## Summary
Severity: Medium
Advisory: GHSA-jxxr-4gwj-5jf2
CVE: CVE-2026-45149
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-jxxr-4gwj-5jf2
Type: github-advisory

## Affected
- npm: `brace-expansion` — affected >=5.0.0 <5.0.6

## Details
The `max` option was being applied too late:

When expanding a single large numeric range like `{1..10000000}`, the sequence generation loop generates all 10 million intermediate elements before the `max` limit is applied With `max=10`, the output is correctly limited to 10 items, but the process still allocates `~505 MB` and spends `~800ms` building the full intermediate array.

### Workaround

Ensure the string to be expanded doesn't contain more values than the desired `max` item count.

## References
- https://github.com/juliangruber/brace-expansion/security/advisories/GHSA-jxxr-4gwj-5jf2
- https://nvd.nist.gov/vuln/detail/CVE-2026-45149
- https://github.com/juliangruber/brace-expansion/commit/c0b095bdc52bc4c36dc88deddbadabc49f8371e5
- https://github.com/juliangruber/brace-expansion
