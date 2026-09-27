# [H] Asciidoctor Infinite Loop vulnerability

## Summary
Severity: High
Advisory: GHSA-qc9p-mjxm-j2wj
CVE: CVE-2018-18385
CWE: CWE-835
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-qc9p-mjxm-j2wj
Type: github-advisory

## Affected
- RubyGems: `asciidoctor` — affected >=0 <1.5.8

## Details
Asciidoctor in versions < 1.5.8 allows remote attackers to cause a denial of service (infinite loop). The loop was caused by the fact that `Parser.next_block` was not exhausting all the lines in the reader as the while loop expected it would. This was happening because the regular expression that detects any list was not agreeing with the regular expression that detects a specific list type. So the line kept getting pushed back onto the reader, hence causing the loop.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-18385
- https://github.com/asciidoctor/asciidoctor/issues/2888
- https://github.com/asciidoctor/asciidoctor
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/asciidoctor/CVE-2018-18385.yml
