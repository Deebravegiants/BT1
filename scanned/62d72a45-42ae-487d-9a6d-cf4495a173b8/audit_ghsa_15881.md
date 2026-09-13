# [M] Possible ReDoS vulnerability in plain_text_for_blockquote_node in Action Text

## Summary
Severity: Medium
Advisory: GHSA-wwhv-wxv9-rpgw
CVE: CVE-2024-47888
CWE: CWE-1333
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2024-10-15
Source: https://github.com/advisories/GHSA-wwhv-wxv9-rpgw
Type: github-advisory

## Affected
- RubyGems: `actiontext` — affected >=6.0.0 <6.1.7.9
- RubyGems: `actiontext` — affected >=7.0.0 <7.0.8.5
- RubyGems: `actiontext` — affected >=7.1.0 <7.1.4.1
- RubyGems: `actiontext` — affected >=7.2.0 <7.2.1.1

## Details
There is a possible ReDoS vulnerability in the plain_text_for_blockquote_node helper in Action Text. This vulnerability has been assigned the CVE identifier CVE-2024-47888.

Impact
------

Carefully crafted text can cause the plain_text_for_blockquote_node helper to take an unexpected amount of time, possibly resulting in a DoS vulnerability. All users running an affected release should either upgrade or apply the relevant patch immediately.

Ruby 3.2 has mitigations for this problem, so Rails applications using Ruby 3.2 or newer are unaffected. Rails 8.0.0.beta1 depends on Ruby 3.2 or greater so is unaffected.


Releases
--------
The fixed releases are available at the normal locations.

Workarounds
-----------
Users can avoid calling `plain_text_for_blockquote_node` or upgrade to Ruby 3.2

Credits
-------

Thanks to [ooooooo_q](https://hackerone.com/ooooooo_q) for the report!

## References
- https://github.com/rails/rails/security/advisories/GHSA-wwhv-wxv9-rpgw
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actiontext/CVE-2024-47888.yml
