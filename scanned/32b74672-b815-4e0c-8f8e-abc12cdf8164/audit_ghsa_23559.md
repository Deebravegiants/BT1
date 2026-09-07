# [H] i18n Vulnerable to Denial of Service Attack

## Summary
Severity: High
Advisory: GHSA-34hf-g744-jw64
CVE: CVE-2014-10077
CWE: CWE-20
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-34hf-g744-jw64
Type: github-advisory

## Affected
- RubyGems: `i18n` — affected >=0 <0.8.0

## Details
Hash#slice in lib/i18n/core_ext/hash.rb in the i18n gem before 0.8.0 for Ruby allows remote attackers to cause a denial of service (application crash) via a call in a situation where :some_key is present in keep_keys but not present in the hash.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-10077
- https://github.com/ruby-i18n/i18n/pull/250/commits/08293a41b34e93824563ca0f5b9b97e7451b6387
- https://github.com/rubysec/ruby-advisory-db/pull/182/files
- https://github.com/svenfuchs/i18n/pull/289
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/i18n/CVE-2014-10077.yml
- https://github.com/svenfuchs/i18n
- https://github.com/svenfuchs/i18n/releases/tag/v0.8.0
- https://lists.debian.org/debian-lts-announce/2018/11/msg00021.html
