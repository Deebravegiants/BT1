# [M] Tinfoil Devise-two-factor does not "burn" a successfully validated one-time password (OTP)

## Summary
Severity: Medium
Advisory: GHSA-x489-jjwm-52g7
CVE: CVE-2015-7225
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-08-28
Source: https://github.com/advisories/GHSA-x489-jjwm-52g7
Type: github-advisory

## Affected
- RubyGems: `devise-two-factor` — affected >=0 <2.0.0

## Details
Tinfoil Devise-two-factor before 2.0.0 does not strictly follow [RFC 6238 § 5.2 ](https://datatracker.ietf.org/doc/html/rfc6238#section-5.2) and does not "burn" a successfully validated one-time password (aka OTP), which allows physically proximate attackers with a target user's login credentials to log in as said user by obtaining the OTP through performing a man-in-the-middle attack between the provider and verifier, or "shoulder surfing", and replaying the OTP in the current time-step.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-7225
- https://github.com/tinfoil/devise-two-factor/issues/45#issuecomment-139335608
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=798466
- https://github.com/advisories/GHSA-x489-jjwm-52g7
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/devise-two-factor/CVE-2015-7225.yml
- https://github.com/tinfoil/devise-two-factor
- https://github.com/tinfoil/devise-two-factor/blob/master/UPGRADING.md
- https://web.archive.org/web/20210122192452/https://www.securityfocus.com/bid/76789
- http://www.openwall.com/lists/oss-security/2015/06/20/4
- http://www.openwall.com/lists/oss-security/2015/09/06/2
- http://www.openwall.com/lists/oss-security/2015/09/17/2
