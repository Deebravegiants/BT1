# [H] Data races in late-static

## Summary
Severity: High
Advisory: GHSA-wr55-mf5c-hhwm
CVE: CVE-2020-36209
CWE: CWE-662
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-wr55-mf5c-hhwm
Type: github-advisory

## Affected
- crates.io: `late-static` — affected >=0 <0.4.0

## Details
Affected versions of this crate implemented Sync for LateStatic with T: Send, so that it is possible to create a data race to a type T: Send + !Sync (e.g. Cell<T>).

This can result in a memory corruption or other kinds of undefined behavior.

The flaw was corrected in commit 11f396c by replacing the T: Send bound to T: Sync bound in the Sync impl for LateStatic<T>.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36209
- https://github.com/Richard-W/late-static/issues/1
- https://github.com/Richard-W/late-static/commit/11f396c
- https://github.com/Richard-W/late-static
- https://rustsec.org/advisories/RUSTSEC-2020-0102.html
