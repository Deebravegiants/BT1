# [M] Possible ReDoS vulnerability in block_format in Action Mailer

## Summary
Severity: Medium
Advisory: GHSA-h47h-mwp9-c6q6
CVE: CVE-2024-47889
CWE: CWE-1333
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2024-10-15
Source: https://github.com/advisories/GHSA-h47h-mwp9-c6q6
Type: github-advisory

## Affected
- RubyGems: `actionmailer` — affected >=3.0.0 <6.1.7.9
- RubyGems: `actionmailer` — affected >=7.0.0 <7.0.8.5
- RubyGems: `actionmailer` — affected >=7.1.0 <7.1.4.1
- RubyGems: `actionmailer` — affected >=7.2.0 <7.2.1.1

## Details
There is a possible ReDoS vulnerability in the block_format helper in Action Mailer. This vulnerability has been assigned the CVE identifier CVE-2024-47889.

Impact
------

Carefully crafted text can cause the block_format helper to take an unexpected amount of time, possibly resulting in a DoS vulnerability. All users running an affected release should either upgrade or apply the relevant patch immediately.

Ruby 3.2 has mitigations for this problem, so Rails applications using Ruby 3.2 or newer are unaffected. Rails 8.0.0.beta1 requires Ruby 3.2 or greater so is unaffected.


Releases
--------
The fixed releases are available at the normal locations.

Workarounds
-----------
Users can avoid calling the `block_format` helper or upgrade to Ruby 3.2

Credits
-------

Thanks to yuki_osaki for the report!

## References
- https://github.com/rails/rails/security/advisories/GHSA-h47h-mwp9-c6q6
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionmailer/CVE-2024-47889.yml
