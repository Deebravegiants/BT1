# [M] Puma's header normalization allows for client to clobber proxy set headers

## Summary
Severity: Medium
Advisory: GHSA-9hf4-67fc-4vf4
CVE: CVE-2024-45614
CWE: CWE-444, CWE-639
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-09-20
Source: https://github.com/advisories/GHSA-9hf4-67fc-4vf4
Type: github-advisory

## Affected
- RubyGems: `puma` — affected >=0 <5.6.9
- RubyGems: `puma` — affected >=6.0.0 <6.4.3

## Details
### Impact

Clients could clobber values set by intermediate proxies (such as X-Forwarded-For) by providing a underscore version of the same header (X-Forwarded_For). Any users trusting headers set by their proxy may be affected. Attackers may be able to downgrade connections to HTTP (non-SSL) or redirect responses, which could cause confidentiality leaks if combined with a separate MITM attack. 

### Patches
v6.4.3/v5.6.9 now discards any headers using underscores if the non-underscore version also exists. Effectively, allowing the proxy defined headers to always win.

### Workarounds
Nginx has a [underscores_in_headers](https://nginx.org/en/docs/http/ngx_http_core_module.html#underscores_in_headers) configuration variable to discard these headers at the proxy level.

Any users that are implicitly trusting the proxy defined headers for security or availability should immediately cease doing so until upgraded to the fixed versions.

## References
- https://github.com/puma/puma/security/advisories/GHSA-9hf4-67fc-4vf4
- https://nvd.nist.gov/vuln/detail/CVE-2024-45614
- https://github.com/puma/puma/commit/cac3fd18cf29ed43719ff5d52d9cfec215f0a043
- https://github.com/puma/puma/commit/f196b23be24712fb8fb16051cc124798cc84f70e
- https://github.com/puma/puma
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/puma/CVE-2024-45614.yml
- https://lists.debian.org/debian-lts-announce/2024/11/msg00004.html
- https://nginx.org/en/docs/http/ngx_http_core_module.html#underscores_in_headers
