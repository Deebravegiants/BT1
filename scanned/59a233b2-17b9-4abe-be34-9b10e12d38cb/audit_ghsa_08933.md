# [H] Phoenix: Long-poll NDJSON body splitting causes large memory allocation

## Summary
Severity: High
Advisory: GHSA-628h-q48j-jr6q
CVE: CVE-2026-32689
CWE: CWE-770
Ecosystem: Hex
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-628h-q48j-jr6q
Type: github-advisory

## Affected
- Hex: `phoenix` — affected >=1.7.0 <1.7.22
- Hex: `phoenix` — affected >=1.8.0 <1.8.6

## Details
### Summary

An unauthenticated denial-of-service vulnerability in Phoenix's long-poll transport allows a remote client to allocate a large amount of memory with a HTTP request. A handful of concurrent requests can be sufficient to let the node run out of memory.

See also https://cna.erlef.org/cves/CVE-2026-32689.html.

### Details

The unoptimised code path exists on the `application/x-ndjson` POST handling in the LongPoll transport. The endpoint requires only a session token, which any client can obtain by issuing a GET to the same URL with a matching `Origin` header, so exploitation is unauthenticated.

### Impact

Anyone who runs a LiveView app with a public Longpoll socket or uses a `Phoenix.Socket` with longpoll option.
Longpoll has been enabled for newly generated Phoenix projects since Phoenix 1.7.11.

## References
- https://github.com/phoenixframework/phoenix/security/advisories/GHSA-628h-q48j-jr6q
- https://nvd.nist.gov/vuln/detail/CVE-2026-32689
- https://github.com/phoenixframework/phoenix/commit/1a67c61ff9ce0a7711662ac7354861917a7c80f7
- https://github.com/phoenixframework/phoenix/commit/912ea181fd247c21dbcc49fb97d0053b947d81bf
- https://cna.erlef.org/cves/CVE-2026-32689.html
- https://github.com/phoenixframework/phoenix
- https://osv.dev/vulnerability/EEF-CVE-2026-32689
