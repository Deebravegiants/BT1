# [H] Diesel vulnerable to Binary Protocol Misinterpretation caused by Truncating or Overflowing Casts

## Summary
Severity: High
Advisory: GHSA-wq9x-qwcq-mmgf
CWE: CWE-89
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-08-23
Source: https://github.com/advisories/GHSA-wq9x-qwcq-mmgf
Type: github-advisory

## Affected
- crates.io: `diesel` — affected >=0 <2.2.3

## Details
The following presentation at this year's DEF CON was brought to our attention on the Diesel Gitter Channel:

> SQL Injection isn't Dead: Smuggling Queries at the Protocol Level  
> <http://web.archive.org/web/20240812130923/https://media.defcon.org/DEF%20CON%2032/DEF%20CON%2032%20presentations/DEF%20CON%2032%20-%20Paul%20Gerste%20-%20SQL%20Injection%20Isn't%20Dead%20Smuggling%20Queries%20at%20the%20Protocol%20Level.pdf>  
> (Archive link for posterity.)
Essentially, encoding a value larger than 4GiB can cause the length prefix in the protocol to overflow, 
causing the server to interpret the rest of the string as binary protocol commands or other data.

It appears Diesel _does_ perform truncating casts in a way that could be problematic, 
for example: <https://github.com/diesel-rs/diesel/blob/ae82c4a5a133db65612b7436356f549bfecda1c7/diesel/src/pg/connection/stmt/mod.rs#L36>

This code has existed essentially since the beginning, 
so it is reasonable to assume that all published versions `<= 2.2.2` are affected.

## Mitigation

The prefered migration to the outlined problem is to update to a Diesel version newer than 2.2.2, which includes 
fixes for the problem. 

As always, you should make sure your application is validating untrustworthy user input. 
Reject any input over 4 GiB, or any input that could _encode_ to a string longer than 4 GiB. 
Dynamically built queries are also potentially problematic if it pushes the message size over this 4 GiB bound.

For web application backends, consider adding some middleware that limits the size of request bodies by default.

## Resolution

Diesel now uses `#[deny]` directives for the following Clippy lints:

* [`cast_possible_truncation`](https://rust-lang.github.io/rust-clippy/master/#/cast_possible_truncation)
* [`cast_possible_wrap`](https://rust-lang.github.io/rust-clippy/master/#/cast_possible_wrap)
* [`cast_sign_loss`](https://rust-lang.github.io/rust-clippy/master/#/cast_sign_loss)

to prevent casts that will lead to precision loss or other trunctations. Additionally we performed an 
audit of the relevant code.

A fix is included in the `2.2.3` release.

## References
- https://github.com/diesel-rs/diesel/pull/4170
- https://github.com/diesel-rs/diesel/commit/9eccd7d6d705ac53618bfd478152e32ec3b4536c
- https://github.com/diesel-rs/diesel
- https://github.com/diesel-rs/diesel/blob/ae82c4a5a133db65612b7436356f549bfecda1c7/diesel/src/pg/connection/stmt/mod.rs#L36
- https://rustsec.org/advisories/RUSTSEC-2024-0365.html
