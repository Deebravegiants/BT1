# [M] Escape Sequence Injection vulnerability in Rack lead to Possible Log Injection

## Summary
Severity: Medium
Advisory: GHSA-8cgq-6mh2-7j6v
CVE: CVE-2025-27111
CWE: CWE-117, CWE-93
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2025-03-04
Source: https://github.com/advisories/GHSA-8cgq-6mh2-7j6v
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=0 <2.2.12
- RubyGems: `rack` — affected >=3.0 <3.0.13
- RubyGems: `rack` — affected >=3.1 <3.1.11

## Details
## Summary

`Rack::Sendfile` can be exploited by crafting input that includes newline characters to manipulate log entries.

## Details

The `Rack::Sendfile` middleware logs unsanitized header values from the `X-Sendfile-Type` header. An attacker can exploit this by injecting escape sequences (such as newline characters) into the header, resulting in log injection.

## Impact

This vulnerability can distort log files, obscure attack traces, and complicate security auditing.

## Mitigation

- Update to the latest version of Rack, or
- Remove usage of `Rack::Sendfile`.

## References
- https://github.com/rack/rack/security/advisories/GHSA-8cgq-6mh2-7j6v
- https://nvd.nist.gov/vuln/detail/CVE-2025-27111
- https://github.com/rack/rack/commit/803aa221e8302719715e224f4476e438f2531a53
- https://github.com/rack/rack/commit/aeac570bb8080ca7b53b7f2e2f67498be7ebd30b
- https://github.com/rack/rack/commit/b13bc6bfc7506aca3478dc5ac1c2ec6fc53f82a3
- https://github.com/rack/rack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2025-27111.yml
- https://lists.debian.org/debian-lts-announce/2025/03/msg00016.html
