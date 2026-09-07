# [M] Gemirro Stored XSS in Gemspec "homepage" value

## Summary
Severity: Medium
Advisory: GHSA-x7p2-x2j6-mwhr
CVE: CVE-2017-16833
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2017-11-29
Source: https://github.com/advisories/GHSA-x7p2-x2j6-mwhr
Type: github-advisory

## Affected
- RubyGems: `gemirro` — affected >=0 <0.16.0

## Details
Stored cross-site scripting (XSS) vulnerability in Gemirro before 0.16.0 allows attackers to inject arbitrary web script via a crafted javascript: URL in the "homepage" value of a ".gemspec" file.
A ".gemspec" file must be created with a JavaScript URL in the homepage  value. This can be used to build a gem for upload to the Gemirro server, in order to achieve stored XSS via the author name hyperlink.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16833
- https://github.com/PierreRambaud/gemirro/commit/9659f9b7ce15a723da8e361bd41b9203b19c97de
- https://github.com/PierreRambaud/gemirro
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/gemirro/CVE-2017-16833.yml
