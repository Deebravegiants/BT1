# [M] Data races in noise_search

## Summary
Severity: Medium
Advisory: GHSA-wxjf-9f4g-3v44
CVE: CVE-2020-36461
CWE: CWE-362, CWE-77
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-wxjf-9f4g-3v44
Type: github-advisory

## Affected
- crates.io: `noise_search` — affected >=0

## Details
Affected versions of the `noise_search` crate unconditionally implement Send/Sync for `MvccRwLock`.
This can lead to data races when types that are either `!Send` or `!Sync` (e.g. `Rc<T>`, `Arc<Cell<_>>`) are contained inside `MvccRwLock` and sent across thread boundaries. The data races can potentially lead to memory corruption (as demonstrated in the PoC from the original report issue).

Also, safe APIs of `MvccRwLock` allow aliasing violations by allowing `&T` and `LockResult<MutexGuard<Box<T>>>` to co-exist in conflicting lifetime regions. The APIs of `MvccRwLock` should either be marked as `unsafe` or `MbccRwLock` should be changed to private or pub(crate).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36461
- https://github.com/pipedown/noise/issues/72
- https://github.com/pipedown/noise
- https://rustsec.org/advisories/RUSTSEC-2020-0141.html
