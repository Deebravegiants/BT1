# [H] Nokogiri CSS selector tokenizer has regular expression backtracking

## Summary
Severity: High
Advisory: GHSA-c4rq-3m3g-8wgx
CVE: CVE-2026-79770
CWE: CWE-1333
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-c4rq-3m3g-8wgx
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=0 <1.19.3

## Details
## Summary

Nokogiri's CSS selector tokenizer contains regular expressions whose construction may result in exponential regex backtracking on adversarial selectors. Three ReDoS vectors are addressed in this release:

1. String-literal tokenization on certain unterminated quoted-string input.
2. String-literal tokenization on a separate class of hex-escape-rich input.
3. Identifier tokenization on hex-escape-rich input.

The public CSS selector methods that funnel through the affected tokenizer are `Nokogiri::CSS.xpath_for`, `Node#css`, `Node#at_css`, `Searchable#search`, and `CSS::Parser#parse`.


## Mitigation

Upgrade to Nokogiri `>= 1.19.3`.

If users are unable to upgrade, two options are available:

- Avoid the use of attacker-controlled text in CSS selectors. Applications that only pass developer-authored selectors to Nokogiri are not directly exposed.
- Set global `Regexp.timeout` (Ruby 3.2+, JRuby 9.4+) to bound parse time.

## Severity

The Nokogiri maintainers have evaluated this as **High Severity** (CVSS 7.5, `AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`).

An attacker able to inject user-supplied text into a CSS selector parse method can cause exponential backtracking, resulting in a potential denial of service.


## Resources

- [CWE-1333: Inefficient Regular Expression Complexity](https://cwe.mitre.org/data/definitions/1333.html)


## Credit

Vector 1 was responsibly reported by @colby-swandale. Vectors 2 and 3 were discovered by @flavorjones during the response to the original report.

## References
- https://github.com/sparklemotion/nokogiri/security/advisories/GHSA-c4rq-3m3g-8wgx
- https://nvd.nist.gov/vuln/detail/CVE-2026-79770
- https://github.com/sparklemotion/nokogiri
- https://www.vulncheck.com/advisories/nokogiri-before-redos-via-css-selector-tokenizer
