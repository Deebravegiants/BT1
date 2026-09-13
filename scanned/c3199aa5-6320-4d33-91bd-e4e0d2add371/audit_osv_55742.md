# [C] Use-after-free in Framed due to lack of pinning

## Summary
Severity: Critical
Advisory: RUSTSEC-2020-0049
Aliases: CVE-2020-35902, GHSA-rqgx-hpg4-456r
Ecosystem: crates.io
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-30
Source: https://osv.dev/vulnerability/RUSTSEC-2020-0049
Type: osv

## Affected
- crates.io: `actix-codec` — affected >=0.0.0-0 <0.3.0-beta.1

## Details
Affected versions of this crate did not require the buffer wrapped in `Framed` to be pinned,
but treated it as if it had a fixed location in memory. This may result in a use-after-free.
 
The flaw was corrected by making the affected functions accept `Pin<&mut Self>` instead of `&mut self`.

## References
- https://crates.io/crates/actix-codec
- https://rustsec.org/advisories/RUSTSEC-2020-0049.html
- https://github.com/actix/actix-net/issues/91
