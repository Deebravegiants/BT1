# [H] Rack allows Percent-encoded cookies to overwrite existing prefixed cookie names

## Summary
Severity: High
Advisory: GHSA-j6w9-fv6q-3q52
CVE: CVE-2020-8184
CWE: CWE-20, CWE-784
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2020-06-24
Source: https://github.com/advisories/GHSA-j6w9-fv6q-3q52
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=0 <2.1.4
- RubyGems: `rack` — affected >=2.2.0 <2.2.3

## Details
A reliance on cookies without validation/integrity check security vulnerability exists in rack < 2.2.3, rack < 2.1.4 that makes it possible for an attacker to forge a secure or host-only cookie prefix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8184
- https://github.com/rack/rack/commit/1f5763de6a9fe515ff84992b343d63c88104654c
- https://hackerone.com/reports/895727
- https://github.com/rack/rack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2020-8184.yml
- https://groups.google.com/g/rubyonrails-security/c/OWtmozPH9Ak
- https://lists.debian.org/debian-lts-announce/2020/07/msg00006.html
- https://lists.debian.org/debian-lts-announce/2023/01/msg00038.html
- https://usn.ubuntu.com/4561-1
