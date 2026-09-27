# [C] Arbitrary file write in actionpack-page_caching gem

## Summary
Severity: Critical
Advisory: GHSA-mg5p-95m9-rmfp
CVE: CVE-2020-8159
CWE: CWE-22
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-05-13
Source: https://github.com/advisories/GHSA-mg5p-95m9-rmfp
Type: github-advisory

## Affected
- RubyGems: `actionpack-page_caching` — affected >=0 <1.2.1

## Details
There is a vulnerability in actionpack_page-caching gem < v1.2.1 that allows an attacker to write arbitrary files to a web server, potentially resulting in remote code execution if the attacker can write unescaped ERB to a view.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8159
- https://github.com/rails/actionpack-page_caching/commit/127da70a559bed4fc573fdb4a6d498a7d5815ce2
- https://groups.google.com/forum/#!topic/rubyonrails-security/CFRVkEytdP8
- https://lists.debian.org/debian-lts-announce/2021/07/msg00019.html
