# [H] Karteek Docsplit vulnerable to OS Command Injection

## Summary
Severity: High
Advisory: GHSA-4fvg-pwv7-v54g
CVE: CVE-2013-1933
CWE: CWE-78
Ecosystem: RubyGems
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-4fvg-pwv7-v54g
Type: github-advisory

## Affected
- RubyGems: `karteek-docsplit` — affected >=0

## Details
The `extract_from_ocr` function in `lib/docsplit/text_extractor.rb` in the Karteek Docsplit (karteek-docsplit) gem 0.5.4 for Ruby allows context-dependent attackers to execute arbitrary commands via shell metacharacters in a PDF filename.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1933
- https://exchange.xforce.ibmcloud.com/vulnerabilities/83277
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/karteek-docsplit/CVE-2013-1933.yml
- http://vapid.dhs.org/advisories/karteek-docsplit-cmd-inject.html
- http://www.openwall.com/lists/oss-security/2013/04/08/15
