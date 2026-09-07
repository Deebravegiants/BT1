# [C] StringIO buffer overread vulnerability

## Summary
Severity: Critical
Advisory: GHSA-v5h6-c2hv-hv3r
CVE: CVE-2024-27280
CWE: CWE-120, CWE-126
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-25
Source: https://github.com/advisories/GHSA-v5h6-c2hv-hv3r
Type: github-advisory

## Affected
- RubyGems: `stringio` — affected >=0 <3.0.1.1

## Details
An issue was discovered in StringIO 3.0.1, as distributed in Ruby 3.0.x through 3.0.6 and 3.1.x through 3.1.4.

The `ungetbyte` and `ungetc` methods on a StringIO can read past the end of a string, and a subsequent call to `StringIO.gets` may return the memory value.

This vulnerability is not affected StringIO 3.0.3 and later, and Ruby 3.2.x and later.

We recommend to update the StringIO gem to version 3.0.3 or later. In order to ensure compatibility with bundled version in older Ruby series, you may update as follows instead:

* For Ruby 3.0 users: Update to `stringio` 3.0.1.1
* For Ruby 3.1 users: Update to `stringio` 3.1.0.2

You can use `gem update stringio` to update it. If you are using bundler, please add `gem "stringio", ">= 3.0.1.2"` to your `Gemfile`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-27280
- https://github.com/ruby/stringio/commit/0e596524097706263d10900ca180898e4a8f5233
- https://github.com/ruby/stringio/commit/c58c5f54f1eab99665ea6a161d29ff6a7490afc8
- https://hackerone.com/reports/1399856
- https://github.com/ruby/stringio
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/stringio/CVE-2024-27280.yml
- https://lists.debian.org/debian-lts-announce/2024/09/msg00000.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/27LUWREIFTP3MQAW7QE4PJM4DPAQJWXF
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XYDHPHEZI7OQXTQKTDZHGZNPIJH7ZV5N
- https://security.netapp.com/advisory/ntap-20250502-0003
- https://www.ruby-lang.org/en/news/2024/03/21/buffer-overread-cve-2024-27280
- http://seclists.org/fulldisclosure/2025/Sep/53
- http://seclists.org/fulldisclosure/2025/Sep/54
- http://seclists.org/fulldisclosure/2025/Sep/55
