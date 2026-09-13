# [H] EventList's From<EventList> conversions can double drop on panic.

## Summary
Severity: High
Advisory: RUSTSEC-2021-0011
Aliases: CVE-2021-25908, GHSA-x3v2-fgr6-3wmm
Ecosystem: crates.io
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-01-04
Source: https://osv.dev/vulnerability/RUSTSEC-2021-0011
Type: osv

## Affected
- crates.io: `fil-ocl` — affected >=0.12.0

## Details
Affected versions of this crate read from a container using `ptr::read` in
`From<EventList>`, and then call a user specified `Into<Event>` function.

This issue can result in a double-free if the user provided function panics.

## References
- https://crates.io/crates/fil-ocl
- https://rustsec.org/advisories/RUSTSEC-2021-0011.html
- https://github.com/cogciprocate/ocl/issues/194
