# [M] qiita-markdown Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-9p29-94hp-8rvc
CVE: CVE-2021-28833
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-08-02
Source: https://github.com/advisories/GHSA-9p29-94hp-8rvc
Type: github-advisory

## Affected
- RubyGems: `qiita-markdown` — affected >=0 <0.34.0

## Details
Increments Qiita::Markdown before 0.34.0 allows XSS via a crafted gist link, a different vulnerability than CVE-2021-28796.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28833
- https://github.com/increments/qiita-markdown/commit/b5d4e60bf537ceb177e70bf91653d29575e1aa21
- https://github.com/increments/qiita-markdown
- https://github.com/increments/qiita-markdown/compare/v0.33.0...v0.34.0
- https://github.com/increments/qiita-markdown/releases
- https://vuln.ryotak.me/advisories/50
