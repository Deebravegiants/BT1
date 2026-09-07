# [H] Rack has an Unbounded-Parameter DoS in Rack::QueryParser

## Summary
Severity: High
Advisory: GHSA-gjh7-p2fx-99vx
CVE: CVE-2025-46727
CWE: CWE-400
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-05-08
Source: https://github.com/advisories/GHSA-gjh7-p2fx-99vx
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=0 <2.2.14
- RubyGems: `rack` — affected >=3.0 <3.0.16
- RubyGems: `rack` — affected >=3.1 <3.1.14

## Details
## Summary

`Rack::QueryParser` parses query strings and `application/x-www-form-urlencoded` bodies into Ruby data structures without imposing any limit on the number of parameters, allowing attackers to send requests with extremely large numbers of parameters.

## Details

The vulnerability arises because `Rack::QueryParser` iterates over each `&`-separated key-value pair and adds it to a Hash without enforcing an upper bound on the total number of parameters. This allows an attacker to send a single request containing hundreds of thousands (or more) of parameters, which consumes excessive memory and CPU during parsing.

## Impact

An attacker can trigger denial of service by sending specifically crafted HTTP requests, which can cause memory exhaustion or pin CPU resources, stalling or crashing the Rack server. This results in full service disruption until the affected worker is restarted.

## Mitigation

- Update to a version of Rack that limits the number of parameters parsed, or
- Use middleware to enforce a maximum query string size or parameter count, or
- Employ a reverse proxy (such as Nginx) to limit request sizes and reject oversized query strings or bodies.

Limiting request body sizes and query string lengths at the web server or CDN level is an effective mitigation.

## References
- https://github.com/rack/rack/security/advisories/GHSA-gjh7-p2fx-99vx
- https://nvd.nist.gov/vuln/detail/CVE-2025-46727
- https://github.com/rack/rack/commit/2bb5263b464b65ba4b648996a579dbd180d2b712
- https://github.com/rack/rack/commit/3f5a4249118d09d199fe480466c8c6717e43b6e3
- https://github.com/rack/rack/commit/cd6b70a1f2a1016b73dc906f924869f4902c2d74
- https://github.com/rack/rack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2025-46727.yml
