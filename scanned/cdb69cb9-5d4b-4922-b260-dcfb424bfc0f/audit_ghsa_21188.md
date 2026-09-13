# [C] Active Record RCE bug with Serialized Columns

## Summary
Severity: Critical
Advisory: GHSA-3hhc-qp5v-9p2j
CVE: CVE-2022-32224
CWE: CWE-502
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-12
Source: https://github.com/advisories/GHSA-3hhc-qp5v-9p2j
Type: github-advisory

## Affected
- RubyGems: `activerecord` — affected >=7.0.0 <7.0.3.1
- RubyGems: `activerecord` — affected >=6.1.0 <6.1.6.1
- RubyGems: `activerecord` — affected >=6.0.0 <6.0.5.1
- RubyGems: `activerecord` — affected >=0 <5.2.8.1

## Details
When serialized columns that use YAML (the default) are deserialized, Rails uses YAML.unsafe_load to convert the YAML data in to Ruby objects. If an attacker can manipulate data in the database (via means like SQL injection), then it may be possible for the attacker to escalate to an RCE.

There are no feasible workarounds for this issue, but other coders (such as JSON) are not impacted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-32224
- https://github.com/rails/rails/commit/611990f1a6c137c2d56b1ba06b27e5d2434dcd6a
- https://discuss.rubyonrails.org/t/cve-2022-32224-possible-rce-escalation-bug-with-serialized-columns-in-active-record/81017
- https://github.com/advisories/GHSA-3hhc-qp5v-9p2j
- https://github.com/rails/rails/commits/main/activerecord
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activerecord/CVE-2022-32224.yml
- https://groups.google.com/g/rubyonrails-security/c/MmFO3LYQE8U
- https://lists.debian.org/debian-lts-announce/2026/05/msg00022.html
