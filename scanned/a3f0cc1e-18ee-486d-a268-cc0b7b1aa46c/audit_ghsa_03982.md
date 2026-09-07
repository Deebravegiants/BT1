# [H] Timing Attack in csrf-lite

## Summary
Severity: High
Advisory: GHSA-hjhr-r3gq-qvp6
CVE: CVE-2016-10535
CWE: CWE-208
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-hjhr-r3gq-qvp6
Type: github-advisory

## Affected
- npm: `csrf-lite` — affected >=0 <0.1.2

## Details
Affected versions of `csrf-lite` are vulnerable to timing attacks as a result of testing CSRF tokens via a fail-early comparison instead of a constant-time comparison. 

Timing attacks remove the exponential increase in entropy gained from increased secret length, by providing per-character feedback on the correctness of a guess via miniscule timing differences.

Under favorable network conditions, an attacker can exploit this to guess the secret in no more than (16*18)288 guesses, instead of the 16^18 guesses required were the timing attack not present. 


## Recommendation

Update to version 0.1.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10535
- https://github.com/isaacs/csrf-lite/pull/1
- https://github.com/advisories/GHSA-hjhr-r3gq-qvp6
- https://www.npmjs.com/advisories/94
