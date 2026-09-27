# [H] Data race in conqueue

## Summary
Severity: High
Advisory: GHSA-368f-29c3-4f2r
CVE: CVE-2020-36437
CWE: CWE-119, CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-368f-29c3-4f2r
Type: github-advisory

## Affected
- crates.io: `conqueue` — affected >=0 <0.4.0

## Details
Affected versions of this crate unconditionally implemented `Send`/`Sync` for `QueueSender<T>`, allowing to send non-Send `T` to other threads by invoking `(&QueueSender<T>).send()`.

This fails to prevent users from creating data races by sending types like `Rc<T>` or `Arc<Cell<T>>` to other threads, which can lead to memory corruption. The flaw was corrected in commit `1e462c3` by imposing `T: Send` to both `Send`/`Sync` impls for `QueueSender<T>`/`QueueReceiver<T>`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36437
- https://github.com/longshorej/conqueue/commit/1e462c32e7933821ddb26dc49fd4ffa5aeca97b8
- https://github.com/longshorej/conqueue
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/conqueue/RUSTSEC-2020-0117.md
- https://rustsec.org/advisories/RUSTSEC-2020-0117.html
