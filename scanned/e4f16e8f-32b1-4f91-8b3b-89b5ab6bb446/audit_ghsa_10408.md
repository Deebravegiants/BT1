# [H] Rack has quadratic complexity in Rack::Utils.select_best_encoding via wildcard Accept-Encoding header

## Summary
Severity: High
Advisory: GHSA-v569-hp3g-36wr
CVE: CVE-2026-34230
CWE: CWE-400, CWE-407
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-v569-hp3g-36wr
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=0 <2.2.23
- RubyGems: `rack` — affected >=3.0.0.beta1 <3.1.21
- RubyGems: `rack` — affected >=3.2.0 <3.2.6

## Details
## Summary

`Rack::Utils.select_best_encoding` processes `Accept-Encoding` values with quadratic time complexity when the header contains many wildcard (`*`) entries. Because this method is used by `Rack::Deflater` to choose a response encoding, an unauthenticated attacker can send a single request with a crafted `Accept-Encoding` header and cause disproportionate CPU consumption on the compression middleware path.

This results in a denial of service condition for applications using `Rack::Deflater`.

## Details

`Rack::Utils.select_best_encoding` expands parsed `Accept-Encoding` values into a list of candidate encodings. When an entry is `*`, the method computes the set of concrete encodings by subtracting the encodings already present in the request:

```ruby
if m == "*"
  (available_encodings - accept_encoding.map(&:first)).each do |m2|
    expanded_accept_encoding << [m2, q, preference]
  end
else
  expanded_accept_encoding << [m, q, preference]
end
```

Because `accept_encoding.map(&:first)` is evaluated inside the loop, it is recomputed for each wildcard entry. If the request contains `N` wildcard entries, this produces repeated scans over the full parsed header and causes quadratic behavior.

After expansion, the method also performs additional work over `expanded_accept_encoding`, including per-entry deletion, which further increases the cost for large inputs.

`Rack::Deflater` invokes this method for each request when the middleware is enabled:

```ruby
Utils.select_best_encoding(ENCODINGS, Utils.parse_encodings(accept_encoding))
```

As a result, a client can trigger this expensive code path simply by sending a large `Accept-Encoding` header containing many repeated wildcard values.

For example, a request with an approximately 8 KB `Accept-Encoding` header containing about 1,000 `*;q=0.5` entries can cause roughly 170 ms of CPU time in a single request on the `Rack::Deflater` path, compared to a negligible baseline for a normal header.

This issue is distinct from CVE-2024-26146. That issue concerned regular expression denial of service during `Accept` header parsing, whereas this issue arises later during encoding selection after the header has already been parsed.

## Impact

Any Rack application using `Rack::Deflater` may be affected.

An unauthenticated attacker can send requests with crafted `Accept-Encoding` headers to trigger excessive CPU usage in the encoding selection logic. Repeated requests can consume worker time disproportionately and reduce application availability.

The attack does not require invalid HTTP syntax or large payload bodies. A single header-sized request is sufficient to reach the vulnerable code path.

## Mitigation

* Update to a patched version of Rack in which encoding selection does not repeatedly rescan the parsed header for wildcard entries.
* Avoid enabling `Rack::Deflater` on untrusted traffic.
* Apply request filtering or header size / format restrictions at the reverse proxy or application boundary to limit abusive `Accept-Encoding` values.

## References
- https://github.com/rack/rack/security/advisories/GHSA-v569-hp3g-36wr
- https://nvd.nist.gov/vuln/detail/CVE-2026-34230
- https://github.com/rack/rack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2026-34230.yml
