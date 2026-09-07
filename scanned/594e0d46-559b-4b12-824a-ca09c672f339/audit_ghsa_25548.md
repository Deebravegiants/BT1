# [M] Improper one time password handling in devise-two-factor

## Summary
Severity: Medium
Advisory: GHSA-jm35-h8q2-73mp
CVE: CVE-2021-43177
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-04-07
Source: https://github.com/advisories/GHSA-jm35-h8q2-73mp
Type: github-advisory

## Affected
- RubyGems: `devise-two-factor` — affected >=0 <4.0.2

## Details
### Impact
As a result of an incomplete fix for CVE-2015-7225, in versions of devise-two-factor prior to 4.0.2 it is possible to reuse a One-Time-Password (OTP) for one (and only one) immediately trailing interval.
 
### Patches
This vulnerability has been patched in version 4.0.2 which was released on March 24th, 2022. Individuals using this package are strongly encouraged to upgrade as soon as possible.

### Credit for discovery
Benoit Côté-Jodoin
Michael Nipper - https://github.com/tinfoil/devise-two-factor/issues/106

## References
- https://github.com/tinfoil/devise-two-factor/security/advisories/GHSA-jm35-h8q2-73mp
- https://nvd.nist.gov/vuln/detail/CVE-2021-43177
- https://github.com/tinfoil/devise-two-factor/issues/106
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/devise-two-factor/CVE-2021-43177.yml
- https://github.com/tinfoil/devise-two-factor
