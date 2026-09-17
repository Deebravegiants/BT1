# [H] Puma PROXY Protocol v1 Parser Allows Remote Memory Exhaustion 

## Summary
Severity: High
Advisory: GHSA-qpgp-93vx-g8v8
CVE: CVE-2026-47736
CWE: CWE-400
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-qpgp-93vx-g8v8
Type: github-advisory

## Affected
- RubyGems: `puma` — affected >=8.0.0 <8.0.2
- RubyGems: `puma` — affected >=5.5.0 <7.2.1

## Details
### Impact

[PROXY protocol support for Puma](https://github.com/puma/puma/issues/2651) was added in version 5.5.0.

When PROXY protocol v1 support is enabled, Puma reads incoming bytes into an internal buffer. It waits for "\r\n" to determine whether a PROXY v1 line is present. If an attacker opens a TCP connection and continuously sends bytes without CRLF, Puma keeps appending to this pre-parse buffer.

This can cause unbounded in-process memory growth and additional CPU cost from repeatedly scanning the growing buffer for CRLF. A single, unauthenticated TCP connection can drive significant memory growth and may cause process/container OOM or degraded availability.

**Only Puma servers using the following non-default config are affected:**

```ruby
   set_remote_address proxy_protocol: :v1
```

### Patches

Users should upgrade to versions 7.2.1 or 8.0.2.

### Workarounds

- Disable PROXY protocol v1 parsing if it is not required:

 ```ruby
   # remove/comment this:
   # set_remote_address proxy_protocol: :v1
 ```

 - Restrict direct network access to Puma listeners using PROXY protocol:
     - Only allow trusted load balancers/reverse proxies to connect.
     - Block arbitrary client TCP access with firewall/security group rules.

### Resources
- [HAProxy PROXY protocol specification](https://www.haproxy.org/download/1.8/doc/proxy-protocol.txt)
- [CWE-400: Uncontrolled Resource Consumption](https://cwe.mitre.org/data/definitions/400.html)
- [CWE-770: Allocation of Resources Without Limits or Throttling](https://cwe.mitre.org/data/definitions/770.html)
- [Puma `set_remote_address` documentation](https://github.com/puma/puma/blob/master/lib/puma/dsl.rb)
- [Puma client PROXY protocol parsing code](https://github.com/puma/puma/blob/master/lib/puma/client.rb)
- [Puma constants, including `PROXY_PROTOCOL_V1_REGEX`](https://github.com/puma/puma/blob/master/lib/puma/const.rb)

## References
- https://github.com/puma/puma/security/advisories/GHSA-qpgp-93vx-g8v8
- https://github.com/puma/puma
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/puma/CVE-2026-47736.yml
- https://www.cve.org/CVERecord?id=CVE-2026-47736
