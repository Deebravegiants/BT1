# [M] Ox gem stack overflow in sax_parse

## Summary
Severity: Medium
Advisory: GHSA-wfwm-chj7-w59r
CVE: CVE-2017-16229
CWE: CWE-125
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-03-05
Source: https://github.com/advisories/GHSA-wfwm-chj7-w59r
Type: github-advisory

## Affected
- RubyGems: `ox` — affected >=0 <2.8.2

## Details
In the Ox gem 2.8.1 for Ruby, the process crashes with a stack-based buffer over-read in the `read_from_str` function in `sax_buf.c` when a crafted input is supplied to `sax_parse`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16229
- https://github.com/ohler55/ox/issues/195
- https://github.com/ohler55/ox
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/ox/CVE-2017-16229.yml
- https://rubygems.org/gems/ox/versions/2.8.1
