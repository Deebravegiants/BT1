# [M] Possible ReDoS vulnerability in HTTP Token authentication in Action Controller

## Summary
Severity: Medium
Advisory: GHSA-vfg9-r3fq-jvx4
CVE: CVE-2024-47887
CWE: CWE-1333
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2024-10-15
Source: https://github.com/advisories/GHSA-vfg9-r3fq-jvx4
Type: github-advisory

## Affected
- RubyGems: `actionpack` — affected >=4.0.0 <6.1.7.9
- RubyGems: `actionpack` — affected >=7.0.0 <7.0.8.5
- RubyGems: `actionpack` — affected >=7.1.0 <7.1.4.1
- RubyGems: `actionpack` — affected >=7.2.0 <7.2.1.1

## Details
There is a possible ReDoS vulnerability in Action Controller's HTTP Token authentication. This vulnerability has been assigned the CVE identifier CVE-2024-47887.

Impact
------

For applications using HTTP Token authentication via `authenticate_or_request_with_http_token` or similar, a carefully crafted header may cause header parsing to take an unexpected amount of time, possibly resulting in a DoS vulnerability. All users running an affected release should either upgrade or apply the relevant patch immediately.

Ruby 3.2 has mitigations for this problem, so Rails applications using Ruby 3.2 or newer are unaffected. Rails 8.0.0.beta1 depends on Ruby 3.2 or greater so is unaffected.

Releases
--------
The fixed releases are available at the normal locations.

Workarounds
-----------
Users on Ruby 3.2 are unaffected by this issue.


Credits
-------
Thanks to [scyoon](https://hackerone.com/scyoon) for reporting

## References
- https://github.com/rails/rails/security/advisories/GHSA-vfg9-r3fq-jvx4
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2024-47887.yml
