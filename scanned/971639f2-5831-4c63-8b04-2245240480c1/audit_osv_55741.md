# [H] Use-after-free in BodyStream due to lack of pinning

## Summary
Severity: High
Advisory: RUSTSEC-2020-0048
Aliases: CVE-2020-35901, GHSA-v3j6-xf77-8r9c
Ecosystem: crates.io
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-01-24
Source: https://osv.dev/vulnerability/RUSTSEC-2020-0048
Type: osv

## Affected
- crates.io: `actix-http` — affected >=0.0.0-0 <2.0.0-alpha.1

## Details
Affected versions of this crate did not require the buffer wrapped in `BodyStream` to be pinned,
but treated it as if it had a fixed location in memory. This may result in a use-after-free.
 
The flaw was corrected by making the trait `MessageBody` require `Unpin`
and making `poll_next()` function accept `Pin<&mut Self>` instead of `&mut self`.

## References
- https://crates.io/crates/actix-http
- https://rustsec.org/advisories/RUSTSEC-2020-0048.html
- https://github.com/actix/actix-web/issues/1321
