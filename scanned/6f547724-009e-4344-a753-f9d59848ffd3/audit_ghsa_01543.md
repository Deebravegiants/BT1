# [H] Directory traversal in Rack::Directory app bundled with Rack

## Summary
Severity: High
Advisory: GHSA-5f9h-9pjv-v6j7
CVE: CVE-2020-8161
CWE: CWE-22, CWE-548
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2020-07-06
Source: https://github.com/advisories/GHSA-5f9h-9pjv-v6j7
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=0 <2.1.3

## Details
A directory traversal vulnerability exists in rack < 2.2.0 that allows an attacker perform directory traversal vulnerability in the Rack::Directory app that is bundled with Rack which could result in information disclosure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8161
- https://github.com/rack/rack/commit/dddb7ad18ed79ca6ab06ccc417a169fde451246e
- https://github.com/rack/rack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2020-8161.yml
- https://groups.google.com/forum/#!topic/ruby-security-ann/T4ZIsfRf2eA
- https://groups.google.com/g/rubyonrails-security/c/IOO1vNZTzPA
- https://lists.debian.org/debian-lts-announce/2020/07/msg00006.html
- https://lists.debian.org/debian-lts-announce/2023/01/msg00038.html
- https://usn.ubuntu.com/4561-1
