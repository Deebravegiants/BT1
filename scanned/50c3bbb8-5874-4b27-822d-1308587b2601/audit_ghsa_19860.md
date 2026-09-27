# [H] Local File Inclusion in Rack::Static

## Summary
Severity: High
Advisory: GHSA-7wqh-767x-r66v
CVE: CVE-2025-27610
CWE: CWE-23
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-10
Source: https://github.com/advisories/GHSA-7wqh-767x-r66v
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=0 <2.2.13
- RubyGems: `rack` — affected >=3.0 <3.0.14
- RubyGems: `rack` — affected >=3.1 <3.1.12

## Details
## Summary

`Rack::Static` can serve files under the specified `root:` even if `urls:` are provided, which may expose other files under the specified `root:` unexpectedly.

## Details

The vulnerability occurs because `Rack::Static` does not properly sanitize user-supplied paths before serving files. Specifically, encoded path traversal sequences are not correctly validated, allowing attackers to access files outside the designated static file directory.

## Impact

By exploiting this vulnerability, an attacker can gain access to all files under the specified `root:` directory, provided they are able to determine then path of the file.

## Mitigation

- Update to the latest version of Rack, or
- Remove usage of `Rack::Static`, or
- Ensure that `root:` points at a directory path which only contains files which should be accessed publicly.

It is likely that a CDN or similar static file server would also mitigate the issue.

## References
- https://github.com/rack/rack/security/advisories/GHSA-7wqh-767x-r66v
- https://nvd.nist.gov/vuln/detail/CVE-2025-27610
- https://github.com/rack/rack/commit/50caab74fa01ee8f5dbdee7bb2782126d20c6583
- https://github.com/rack/rack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2025-27610.yml
- https://lists.debian.org/debian-lts-announce/2025/03/msg00016.html
