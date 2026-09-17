# [M] Mongrel vulnerable to directory traversal via double-encoded sequences

## Summary
Severity: Medium
Advisory: GHSA-m7r6-43v2-49vf
CVE: CVE-2007-6612
CWE: CWE-22
Ecosystem: RubyGems
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-m7r6-43v2-49vf
Type: github-advisory

## Affected
- RubyGems: `mongrel` — affected >=1.0.4 <1.0.5
- RubyGems: `mongrel` — affected >=1.1.0 <1.1.3

## Details
Directory traversal vulnerability in DirHandler (lib/mongrel/handlers.rb) in Mongrel 1.0.4 (1.0.3 and prior are not affected) and 1.1.x before 1.1.3 allows remote attackers to read arbitrary files via an HTTP request containing double-encoded sequences (`.%252e`).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-6612
- https://github.com/mongrel/mongrel
- https://lists.apple.com/archives/security-announce/2008//May/msg00001.html
- https://web.archive.org/web/20080111034049/http://rubyforge.org/pipermail/mongrel-users/2007-December/004743.html
- https://web.archive.org/web/20200301091534/http://www.securityfocus.com/bid/27133
