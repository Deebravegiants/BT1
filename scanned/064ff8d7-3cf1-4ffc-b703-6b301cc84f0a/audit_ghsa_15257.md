# [M] fugit parse and parse_nat stall on lengthy input

## Summary
Severity: Medium
Advisory: GHSA-2m96-52r3-2f3g
CVE: CVE-2024-43380
CWE: CWE-400
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-08-19
Source: https://github.com/advisories/GHSA-2m96-52r3-2f3g
Type: github-advisory

## Affected
- RubyGems: `fugit` — affected >=0 <1.11.1

## Details
### Impact

The fugit "natural" parser, that turns "every wednesday at 5pm" into "0 17 * * 3", accepted any length of input and went on attempting to parse it, not returning promptly, as expected. The parse call could hold the thread with no end in sight.

Fugit dependents that do not check (user) input length for plausability are impacted.

### Patches

Problem was reported in #104 and the fix was released in [fugit 1.11.1](https://rubygems.org/gems/fugit/versions/1.11.1)

### Workarounds

By making sure that `Fugit.parse(s)`, `Fugit.do_parse(s)`, `Fugit.parse_nat(s)`, `Fugit.do_parse_nat(s)`, `Fugit::Nat.parse(s)`, and `Fugit::Nat.do_parse(s)` are not fed strings too long. 1000 chars feels ok, while 10_000 chars makes it stall.

In fewer words, making sure those fugit methods are not fed unvetted input strings.

### References

gh-104

## References
- https://github.com/floraison/fugit/security/advisories/GHSA-2m96-52r3-2f3g
- https://nvd.nist.gov/vuln/detail/CVE-2024-43380
- https://github.com/floraison/fugit/issues/104
- https://github.com/floraison/fugit/commit/ad2c1c9c737213d585fff0b51c927d178b2c05a5
- https://github.com/floraison/fugit
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/fugit/CVE-2024-43380.yml
