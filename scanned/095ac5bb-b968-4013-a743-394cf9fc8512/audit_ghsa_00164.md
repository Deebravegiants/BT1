# [H] private_address_check contains race condition

## Summary
Severity: High
Advisory: GHSA-2xvj-j3qh-x8c3
CVE: CVE-2018-3759
CWE: CWE-362
Ecosystem: RubyGems
Published: 2018-07-31
Source: https://github.com/advisories/GHSA-2xvj-j3qh-x8c3
Type: github-advisory

## Affected
- RubyGems: `private_address_check` — affected >=0 <0.5.0

## Details
The private_address_check ruby gem before 0.5.0 is vulnerable to a time-of-check time-of-use (TOCTOU) race condition due to the address the socket uses not being checked. DNS entries with a TTL of 0 can trigger this case where the initial resolution is a public address but the subsequent resolution is a private address.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3759
- https://github.com/jtdowney/private_address_check/commit/4068228187db87fea7577f7020099399772bb147
- https://github.com/advisories/GHSA-2xvj-j3qh-x8c3
- https://github.com/jtdowney/private_address_check
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/private_address_check/CVE-2018-3759.yml
