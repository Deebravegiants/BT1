# [M] Diesel: Possible unaligned data access for implementations of `SqliteAggregate`

## Summary
Severity: Medium
Advisory: GHSA-q8x8-jrhj-fh9p
CWE: CWE-188
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-q8x8-jrhj-fh9p
Type: github-advisory

## Affected
- crates.io: `diesel` — affected >=0 <2.3.8

## Details
Diesel allows to register custom aggregate SQL functions for SQLite via the `SqliteAggregate` interface.

To store an instance of the custom aggregate processor Diesel relied on the `sqlite3_aggregate_context` function provided by sqlite. This function doesn't provide any guarantees about alignment of the returned allocation, which in turn can lead to problems if the type implementing requires a special alignment, e.g. via a custom `#[align(x)]` attribute on the type implementing this trait. This affects any user of `SqliteAggregate` that registers the custom aggregate function with an SQLite connection, while using a non-standard alignment on the type implementing this trait.

## Mitigation

The preferred mitigation to the outlined problem is to update to a Diesel version 2.3.8 or newer, which includes fixes for the problem.

## Resolution

Diesel now allocates the corresponding memory on Rust side to get a correctly aligned allocation.

## References
- https://github.com/diesel-rs/diesel/pull/5042
- https://github.com/diesel-rs/diesel
- https://rustsec.org/advisories/RUSTSEC-2026-0137.html
