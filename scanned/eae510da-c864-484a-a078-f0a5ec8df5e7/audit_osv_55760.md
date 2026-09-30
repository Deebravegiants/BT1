# [H] Empty NIP-50 search filters can panic

## Summary
Severity: High
Advisory: RUSTSEC-2026-0230
Ecosystem: crates.io
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/RUSTSEC-2026-0230
Type: osv

## Affected
- crates.io: `nostr` — affected >=0.0.0-0 <0.44.7

## Details
The NIP-50 event-matching path searched event content with
`slice::windows(search.len())`. An empty search string therefore called
`slice::windows(0)`, which always panics instead of returning a match result.

A remote client able to submit filters to an application using this matcher could
trigger the panic with an empty NIP-50 search value. This includes clients querying an
SDK local relay. Depending on the application's panic configuration and task
isolation, the crafted filter could terminate request processing, a runtime worker, or
the entire process, causing denial of service. No confidentiality or integrity impact
is known.

Empty searches are now handled before the substring search, so the matcher returns a
defined result without constructing a zero-sized window or panicking.

## References
- https://crates.io/crates/nostr
- https://rustsec.org/advisories/RUSTSEC-2026-0230.html
- https://github.com/nostrdevkit/nostr/commit/29182657bc54ac18564597e4414f08c3e4e9aa0a
