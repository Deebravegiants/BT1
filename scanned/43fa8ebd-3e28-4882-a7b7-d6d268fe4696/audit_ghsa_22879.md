# [C] Publify vulnerable to cross site scripting

## Summary
Severity: Critical
Advisory: GHSA-3hwx-c6cp-q972
CVE: CVE-2022-1811
CWE: CWE-434, CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-3hwx-c6cp-q972
Type: github-advisory

## Affected
- RubyGems: `publify_core` — affected >=0 <9.2.9

## Details
Unrestricted file upload allowed the attacker to manipulate the request and bypass the protection of HTML files using a text file. Stored XSS may be obtained.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1811
- https://github.com/publify/publify/commit/0fb6b027fbaf17f6a6551f2148482a03eac12927
- https://github.com/publify/publify
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/publify_core/CVE-2022-1811.yml
- https://huntr.dev/bounties/4d97f665-c9f1-4c38-b774-692255a7c44c
