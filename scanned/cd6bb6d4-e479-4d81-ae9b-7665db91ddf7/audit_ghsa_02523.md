# [H] Data races in libsbc

## Summary
Severity: High
Advisory: GHSA-f6g6-54hm-fhxv
CVE: CVE-2020-36440
CWE: CWE-119, CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-f6g6-54hm-fhxv
Type: github-advisory

## Affected
- crates.io: `libsbc` — affected >=0 <0.1.5

## Details
Affected versions of this crate implements `Send` for `Decoder<R>` for any `R: Read`. This allows `Decoder<R>` to contain `R: !Send` and carry (move) it to another thread.

This can result in undefined behavior such as memory corruption from data race on `R`, or dropping `R = MutexGuard<_>` from a thread that didn't lock the mutex.

The flaw was corrected in commit a34d6e1 by adding trait bound `R: Send` to the `Send` impl for `Decoder<R>`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36440
- https://github.com/mvertescher/libsbc-rs/commit/a34d6e1
- https://github.com/mvertescher/libsbc-rs
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/libsbc/RUSTSEC-2020-0120.md
- https://rustsec.org/advisories/RUSTSEC-2020-0120.html
