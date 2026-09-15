# [M] bcrypt-ruby has an Integer Overflow that Causes Zero Key-Strengthening Iterations at Cost=31 on JRuby

## Summary
Severity: Medium
Advisory: GHSA-f27w-vcwj-c954
CVE: CVE-2026-33306
CWE: CWE-190
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:L/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-f27w-vcwj-c954
Type: github-advisory

## Affected
- RubyGems: `bcrypt` — affected >=0 <3.1.22

## Details
### Impact

An integer overflow in the Java BCrypt implementation for JRuby can cause zero iterations in the strengthening loop.  Impacted applications must be setting the cost to 31 to see this happen.

The JRuby implementation of bcrypt-ruby (`BCrypt.java`) computes the key-strengthening round count as a signed 32-bit integer. When `cost=31` (the maximum allowed by the gem), signed integer overflow causes the round count to become negative, and the strengthening loop executes **zero iterations**. This collapses bcrypt from 2^31 rounds of exponential key-strengthening to effectively constant-time computation — only the initial EksBlowfish key setup and final 64x encryption phase remain.

The resulting hash looks valid (`$2a$31$...`) and verifies correctly via `checkpw`, making the weakness invisible to the application. This issue is triggered only when cost=31 is used or when verifying a `$2a$31$` hash.

### Patches

This problem has been fixed in version 3.1.22

### Workarounds

Set the cost to something less than 31.

## References
- https://github.com/bcrypt-ruby/bcrypt-ruby/security/advisories/GHSA-f27w-vcwj-c954
- https://nvd.nist.gov/vuln/detail/CVE-2026-33306
- https://github.com/bcrypt-ruby/bcrypt-ruby/commit/831ce64cb0a9502130fa93a28bfd9527a5fa45c4
- https://github.com/bcrypt-ruby/bcrypt-ruby
- https://github.com/bcrypt-ruby/bcrypt-ruby/releases/tag/v3.1.22
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/bcrypt/CVE-2026-33306.yml
