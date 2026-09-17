# [M] Mail Gem Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-cj92-c4fj-w9c5
CVE: CVE-2012-2139
CWE: CWE-22
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-cj92-c4fj-w9c5
Type: github-advisory

## Affected
- RubyGems: `mail` — affected >=0 <2.4.4

## Details
Directory traversal vulnerability in `lib/mail/network/delivery_methods/file_delivery.rb` in the Mail gem before 2.4.4 for Ruby allows remote attackers to read arbitrary files via a `..` (dot dot) in the to parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-2139
- https://github.com/mikel/mail/commit/29aca25218e4c82991400eb9b0c933626aefc98f
- https://bugzilla.novell.com/show_bug.cgi?id=759092
- https://bugzilla.redhat.com/show_bug.cgi?id=816352
- https://github.com/mikel/mail
- http://lists.fedoraproject.org/pipermail/package-announce/2012-May/080645.html
- http://lists.fedoraproject.org/pipermail/package-announce/2012-May/080648.html
- http://lists.fedoraproject.org/pipermail/package-announce/2012-May/080747.html
- http://www.openwall.com/lists/oss-security/2012/04/25/8
- http://www.openwall.com/lists/oss-security/2012/04/26/1
