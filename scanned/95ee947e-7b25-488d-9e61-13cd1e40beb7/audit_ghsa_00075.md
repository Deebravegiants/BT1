# [M] Gollum Exposure of Sensitive Information

## Summary
Severity: Medium
Advisory: GHSA-m2q3-53fq-7h66
CVE: CVE-2015-7314
CWE: CWE-200
Ecosystem: RubyGems
Published: 2018-08-28
Source: https://github.com/advisories/GHSA-m2q3-53fq-7h66
Type: github-advisory

## Affected
- RubyGems: `gollum` — affected >=0 <4.0.1

## Details
The Precious module in gollum before 4.0.1 allows remote attackers to read arbitrary files by leveraging the lack of a certain temporary-file check.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-7314
- https://github.com/gollum/gollum/issues/1070
- https://github.com/gollum/gollum/commit/ce68a88293ce3b18c261312392ad33a88bb69ea1
- https://github.com/gollum/gollum
- http://jvn.jp/en/jp/JVN27548431/index.html
- http://jvndb.jvn.jp/jvndb/JVNDB-2015-000149
- http://www.openwall.com/lists/oss-security/2015/09/22/12
