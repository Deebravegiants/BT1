# [C] geokit-rails Command Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-7xvc-v44j-46fh
CVE: CVE-2023-26153
CWE: CWE-502, CWE-77
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-06
Source: https://github.com/advisories/GHSA-7xvc-v44j-46fh
Type: github-advisory

## Affected
- RubyGems: `geokit-rails` — affected >=0 <2.5.0

## Details
Versions of the package geokit-rails before 2.5.0 are vulnerable to Command Injection due to unsafe deserialisation of YAML within the 'geo_location' cookie. This issue can be exploited remotely via a malicious cookie value.

**Note:**

 An attacker can use this vulnerability to execute commands on the host system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26153
- https://github.com/geokit/geokit-rails/commit/7ffc5813e57f6f417987043e1039925fd0865c43
- https://github.com/geokit/geokit-rails/commit/a93dfe49fb9aeae7164e2f8c4041450a04b5482f
- https://gist.github.com/CalumHutton/b7aa1c2e71c8d4386463ac14f686901d
- https://github.com/advisories/GHSA-7xvc-v44j-46fh
- https://github.com/geokit/geokit-rails
- https://github.com/geokit/geokit-rails/blob/master/lib/geokit-rails/ip_geocode_lookup.rb#L37
- https://github.com/geokit/geokit-rails/blob/master/lib/geokit-rails/ip_geocode_lookup.rb%23L37
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/geokit-rails/CVE-2023-26153.yml
- https://security.snyk.io/vuln/SNYK-RUBY-GEOKITRAILS-5920323
