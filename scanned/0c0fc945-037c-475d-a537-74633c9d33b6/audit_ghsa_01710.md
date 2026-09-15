# [H] Circumvention of file size limits in ActiveStorage

## Summary
Severity: High
Advisory: GHSA-m42x-37p3-fv5w
CVE: CVE-2020-8162
CWE: CWE-434, CWE-602
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2020-05-26
Source: https://github.com/advisories/GHSA-m42x-37p3-fv5w
Type: github-advisory

## Affected
- RubyGems: `activestorage` — affected >=5.0.0 <5.2.4.3
- RubyGems: `activestorage` — affected >=6.0.0 <6.0.3.1

## Details
There is a vulnerability in ActiveStorage's S3 adapter that allows the Content-Length of a direct file upload to be modified by an end user.

Versions Affected:  rails < 5.2.4.2, rails < 6.0.3.1
Not affected:       Applications that do not use the direct upload functionality of the ActiveStorage S3 adapter.
Fixed Versions:     rails >= 5.2.4.3, rails >= 6.0.3.1

Impact
------

Utilizing this vulnerability, an attacker can control the Content-Length of an S3 direct upload URL without receiving a new signature from the server. This could be used to bypass controls in place on the server to limit upload size.

Workarounds
-----------

This is a low-severity security issue. As such, no workaround is necessarily until such time as the application can be upgraded.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8162
- https://github.com/aws/aws-sdk-ruby/issues/2098
- https://hackerone.com/reports/789579
- https://github.com/aws/aws-sdk-ruby
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activestorage/CVE-2020-8162.yml
- https://groups.google.com/forum/#!topic/rubyonrails-security/PjU3946mreQ
- https://groups.google.com/g/rubyonrails-security/c/PjU3946mreQ
- https://www.debian.org/security/2020/dsa-4766
