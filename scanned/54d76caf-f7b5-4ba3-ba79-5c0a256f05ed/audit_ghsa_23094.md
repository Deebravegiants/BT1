# [M] xapian-core Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7qw4-w7hf-22q3
CVE: CVE-2018-0499
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-7qw4-w7hf-22q3
Type: github-advisory

## Affected
- RubyGems: `xapian-core` — affected >=0 <1.4.6

## Details
A cross-site scripting vulnerability in `queryparser/termgenerator_internal.cc` in Xapian xapian-core before 1.4.6 exists due to incomplete HTML escaping by `Xapian::MSet::snippet()`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-0499
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/xapian-core/CVE-2018-0499.yml
- https://lists.xapian.org/pipermail/xapian-discuss/2018-July/009652.html
- https://trac.xapian.org/wiki/SecurityFixes/2018-07-02
- https://usn.ubuntu.com/3709-1
