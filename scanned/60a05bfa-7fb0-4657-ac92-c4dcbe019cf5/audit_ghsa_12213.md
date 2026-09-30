# [H] Aescrypt does not sufficiently use random values

## Summary
Severity: High
Advisory: GHSA-4c4w-3q45-hp9j
CVE: CVE-2013-7463
CWE: CWE-330
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-4c4w-3q45-hp9j
Type: github-advisory

## Affected
- RubyGems: `aescrypt` — affected >=0

## Details
The aescrypt gem 1.0.0 for Ruby does not randomize the CBC IV for use with the AESCrypt.encrypt and AESCrypt.decrypt functions, which allows attackers to defeat cryptographic protection mechanisms via a chosen plaintext attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7463
- https://github.com/Gurpartap/aescrypt/issues/4
- https://github.com/Gurpartap/aescrypt
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/aescrypt/CVE-2013-7463.yml
- https://web.archive.org/web/20200227173428/http://www.securityfocus.com/bid/98035
