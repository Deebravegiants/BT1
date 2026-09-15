# [H] lynx doesn't properly sanitize user input and exposes database password to unauthorized users

## Summary
Severity: High
Advisory: GHSA-94cq-7ccq-cmcm
CVE: CVE-2014-5002
CWE: CWE-200
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-01-24
Source: https://github.com/advisories/GHSA-94cq-7ccq-cmcm
Type: github-advisory

## Affected
- RubyGems: `lynx` — affected >=0 <1.0.0

## Details
The lynx gem prior to 1.0.0 for Ruby places the configured password on command lines, which allows local users to obtain sensitive information by listing processes.

As of version 1.0.0, lynx no longer supports a `--password` option. Passwords are only configured in a configuration file, so it's no longer possible to expose passwords on the command line.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-5002
- https://github.com/panthomakos/lynx/issues/3
- https://github.com/panthomakos/lynx
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/lynx/CVE-2014-5002.yml
- http://www.openwall.com/lists/oss-security/2014/07/07/23
- http://www.openwall.com/lists/oss-security/2014/07/17/5
- http://www.vapid.dhs.org/advisories/lynx-0.2.0.html
