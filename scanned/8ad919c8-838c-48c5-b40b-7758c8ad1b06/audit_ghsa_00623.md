# [M] rails-html-sanitizer Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-px3r-jm9g-c8w8
CVE: CVE-2018-3741
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-04-26
Source: https://github.com/advisories/GHSA-px3r-jm9g-c8w8
Type: github-advisory

## Affected
- RubyGems: `rails-html-sanitizer` — affected >=0 <1.0.4

## Details
There is a possible XSS vulnerability in all rails-html-sanitizer gem versions below 1.0.4 for Ruby. The gem allows non-whitelisted attributes to be present in sanitized output when input with specially-crafted HTML fragments, and these attributes can lead to an XSS attack on target applications. This issue is similar to CVE-2018-8048 in Loofah. All users running an affected release should either upgrade or use one of the workarounds immediately.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3741
- https://github.com/rails/rails-html-sanitizer/commit/f3ba1a839a35f2ba7f941c15e239a1cb379d56ae
- https://github.com/rails/rails-html-sanitizer
