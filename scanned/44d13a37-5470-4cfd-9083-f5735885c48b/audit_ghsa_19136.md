# [M] Possible Log Injection in Rack::CommonLogger

## Summary
Severity: Medium
Advisory: GHSA-7g2v-jj9q-g3rg
CVE: CVE-2025-25184
CWE: CWE-117, CWE-93
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-02-12
Source: https://github.com/advisories/GHSA-7g2v-jj9q-g3rg
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=0 <2.2.11
- RubyGems: `rack` — affected >=3.0 <3.0.12
- RubyGems: `rack` — affected >=3.1 <3.1.10

## Details
## Summary

`Rack::CommonLogger` can be exploited by crafting input that includes newline characters to manipulate log entries. The supplied proof-of-concept demonstrates injecting malicious content into logs.

## Details

When a user provides the authorization credentials via `Rack::Auth::Basic`, if success, the username will be put in `env['REMOTE_USER']` and later be used by `Rack::CommonLogger` for logging purposes.

The issue occurs when a server intentionally or unintentionally allows a user creation with the username contain CRLF and white space characters, or the server just want to log every login attempts. If an attacker enters a username with CRLF character, the logger will log the malicious username with CRLF characters into the logfile.

## Impact

Attackers can break log formats or insert fraudulent entries, potentially obscuring real activity or injecting malicious data into log files.

## Mitigation

- Update to the latest version of Rack.

## References
- https://github.com/rack/rack/security/advisories/GHSA-7g2v-jj9q-g3rg
- https://nvd.nist.gov/vuln/detail/CVE-2025-25184
- https://github.com/rack/rack/commit/074ae244430cda05c27ca91cda699709cfb3ad8e
- https://github.com/rack/rack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2025-25184.yml
- https://lists.debian.org/debian-lts-announce/2025/03/msg00016.html
