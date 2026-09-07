# [M] Spree uses a hardcoded hash value

## Summary
Severity: Medium
Advisory: GHSA-g466-57gh-cqfw
CVE: CVE-2008-7311
Ecosystem: RubyGems
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-g466-57gh-cqfw
Type: github-advisory

## Affected
- RubyGems: `spree` — affected >=0 <0.4.0

## Details
The session cookie store implementation in Spree 0.2.0 uses a hardcoded `config.action_controller_session` hash value (aka secret key), which makes it easier for remote attackers to bypass cryptographic protection mechanisms by leveraging an application that contains this value within the `config/environment.rb` file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-7311
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/spree/CVE-2008-7311.yml
- https://github.com/spree/spree
- https://spreecommerce.com/blog/security-vulernability-session-cookie-store
- https://web.archive.org/web/20090306033106/http://support.spreehq.org/issues/show/63
- https://web.archive.org/web/20100309050152/http://rubygems.org/gems/spree/versions
- https://web.archive.org/web/20101128024939/http://spreecommerce.com/blog/2008/08/12/security-vulernability-session-cookie-store
- http://spreecommerce.com/blog/2008/08/12/security-vulernability-session-cookie-store
