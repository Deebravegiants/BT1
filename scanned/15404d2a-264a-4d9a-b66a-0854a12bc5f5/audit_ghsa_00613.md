# [H] Rack vulnerable to Denial of Service

## Summary
Severity: High
Advisory: GHSA-hg78-4f6x-99wq
CVE: CVE-2018-16470
CWE: CWE-400
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-11-15
Source: https://github.com/advisories/GHSA-hg78-4f6x-99wq
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=2.0.4 <2.0.6

## Details
There is a possible DoS vulnerability in the multipart parser in Rack before 2.0.6. Specially crafted requests can cause the multipart parser to enter a pathological state, causing the parser to use CPU resources disproportionate to the request size.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16470
- https://access.redhat.com/errata/RHSA-2019:3172
- https://github.com/rack/rack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2018-16470.yml
- https://groups.google.com/forum/#!msg/rubyonrails-security/U_x-YkfuVTg/xhvYAmp6AAAJ
- https://groups.google.com/forum/#!topic/ruby-security-ann/Dz4sRl-ktKk
