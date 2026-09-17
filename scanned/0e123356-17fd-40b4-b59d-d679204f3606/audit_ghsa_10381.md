# [M] Buffer Overflow in Zlib::GzipReader ungetc via large input leads to memory corruption

## Summary
Severity: Medium
Advisory: GHSA-g857-hhfv-j68w
CVE: CVE-2026-27820
CWE: CWE-120
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-g857-hhfv-j68w
Type: github-advisory

## Affected
- RubyGems: `zlib` — affected >=3.2.0 <3.2.3
- RubyGems: `zlib` — affected >=3.1.0 <3.1.2
- RubyGems: `zlib` — affected >=0 <3.0.1

## Details
### Details

A buffer overflow vulnerability exists in `Zlib::GzipReader`.

The `zstream_buffer_ungets` function prepends caller-provided bytes ahead of previously produced output but fails to guarantee the backing Ruby string has enough capacity before the memmove shifts the existing data. This can lead to memory corruption when the buffer length exceeds capacity.

### Recommended action

We recommend to update the `zlib` gem to version 3.2.3 or later. In order to ensure compatibility with bundled version in older Ruby series, you may update as follows instead:

* For Ruby 3.2 users: Update to zlib 3.0.1
* For Ruby 3.3 users: Update to zlib 3.1.2

You can use gem update zlib to update it. If you are using bundler, please add `gem "zlib", ">= 3.2.3"` to your Gemfile.

### Affected versions

zlib gem 3.2.2 or lower

### Credits

[calysteon](https://hackerone.com/calysteon)

### References

* https://hackerone.com/reports/3467067

## References
- https://github.com/ruby/zlib/security/advisories/GHSA-g857-hhfv-j68w
- https://nvd.nist.gov/vuln/detail/CVE-2026-27820
- https://hackerone.com/reports/3467067
- https://github.com/ruby/zlib
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/zlib/CVE-2026-27820.yml
- https://www.ruby-lang.org/en/news/2026/03/05/buffer-overflow-zlib-cve-2026-27820
