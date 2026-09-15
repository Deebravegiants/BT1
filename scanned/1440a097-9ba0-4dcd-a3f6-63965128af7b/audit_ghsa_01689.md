# [H] Information disclosure issue in Active Resource

## Summary
Severity: High
Advisory: GHSA-46j2-xjgp-jrfm
CVE: CVE-2020-8151
CWE: CWE-200, CWE-863
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-05-21
Source: https://github.com/advisories/GHSA-46j2-xjgp-jrfm
Type: github-advisory

## Affected
- RubyGems: `activeresource` — affected >=3.0.0.rc <5.1.1

## Details
There is a possible information disclosure issue in Active Resource <v5.1.1 that could allow an attacker to create specially crafted requests to access data in an unexpected way and possibly leak information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8151
- https://github.com/rails/activeresource/commit/0de18f7e96fa90bbf23b16ac11980bc2cb6a716e
- https://github.com/rails/rails/commit/0e969bdaf8ff2e3384350687aa0b583f94d6dfbc
- https://github.com/rails/activeresource
- https://groups.google.com/forum/#!topic/rubyonrails-security/pktoF4VmiM8
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/P7B7A4H22DZ522HLDS3JX3NX2CXIOZSR
