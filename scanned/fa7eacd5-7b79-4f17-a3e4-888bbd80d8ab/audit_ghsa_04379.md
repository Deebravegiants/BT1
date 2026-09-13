# [H] Puma PROXY Protocol v1 Accepts Repeated Protocol Headers on Persistent Connections

## Summary
Severity: High
Advisory: GHSA-2vqw-3mp8-cgmx
CVE: CVE-2026-47737
CWE: CWE-290, CWE-345
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-2vqw-3mp8-cgmx
Type: github-advisory

## Affected
- RubyGems: `puma` — affected >=8.0.0 <8.0.2
- RubyGems: `puma` — affected >=5.5.0 <7.2.1

## Details
### Impact

Puma is vulnerable to source IP spoofing when `set_remote_address proxy_protocol: :v1` is enabled and persistent connections are used.

PROXY protocol v1 is a connection-level protocol. [Support was added to Puma in v5.5.0](https://github.com/puma/puma/issues/2651). A proxy sends one PROXY header at the beginning of a TCP connection, before any HTTP data. Puma incorrectly re-parsed PROXY protocol headers after each keep-alive request on the same connection. An attacker able to send HTTP requests through a trusted proxy could therefore inject a second PROXY header between HTTP requests. Puma would treat the injected header as authoritative for the next request and overwrite `REMOTE_ADDR`.

This can mislead applications or middleware that use `REMOTE_ADDR` for security decisions, rate limiting, auditing, or allow/deny lists.

**Only deployments that explicitly enable PROXY protocol v1 are affected**, and will have set:

```ruby
set_remote_address proxy_protocol: :v1
```

Puma's default configuration is not affected. Deployments that do not use persistent connections to Puma are also not expected to be affected by this issue.

### Patches

Users should upgrade to versions 7.2.1 or 8.0.2.

### Workarounds

Disable PROXY protocol v1 parsing if it is not required:

 ```ruby
   # remove/comment this:
   # set_remote_address proxy_protocol: :v1
 ```

Users can also disable persistent connections to Puma, for example:

```ruby
enable_keep_alives false
```

### References

- [HAProxy PROXY protocol specification](https://www.haproxy.org/download/1.8/doc/proxy-protocol.txt)
- [CVE-2025-31135 / GHSA-c2c3-pqw5-5p7c: go-guerrilla repeated PROXY command source IP spoofing](https://github.com/phires/go-guerrilla/security/advisories/GHSA-c2c3-pqw5-5p7c)
- [Puma `set_remote_address` documentation](https://github.com/puma/puma/blob/master/lib/puma/dsl.rb)

## References
- https://github.com/puma/puma/security/advisories/GHSA-2vqw-3mp8-cgmx
- https://github.com/puma/puma
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/puma/CVE-2026-47737.yml
- https://www.cve.org/CVERecord/SearchResults?query=CVE-2026-47737
