# [H] Wrong memory orderings violates mutual exclusion in spin

## Summary
Severity: High
Advisory: GHSA-hv7x-f3pv-gpwr
CVE: CVE-2019-16137
CWE: CWE-662
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-hv7x-f3pv-gpwr
Type: github-advisory

## Affected
- crates.io: `spin` — affected >=0 <0.5.2

## Details
Wrong memory orderings inside the RwLock implementation allow for two writers to acquire the lock at the same time. The drop implementation used Ordering::Relaxed, which allows the compiler or CPU to reorder a mutable access on the locked data after the lock has been yielded.

Only users of the RwLock implementation are affected. Users of Once (including users of lazy_static with the spin_no_std feature enabled) are NOT affected.

On strongly ordered CPU architectures like x86, the only real way that this would lead to a memory corruption is if the compiler reorders an access after the lock is yielded, which is possible but in practice unlikely. It is a more serious issue on weakly ordered architectures such as ARM which, except in the presence of certain instructions, allow the hardware to decide which accesses are seen at what times. Therefore on an ARM system it is likely that using the wrong memory ordering would result in a memory corruption, even if the compiler itself doesn't reorder the memory accesses in a buggy way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16137
- https://github.com/mvdnes/spin-rs/issues/65
- https://github.com/mvdnes/spin-rs/pull/66
- https://github.com/mvdnes/spin-rs
- https://rustsec.org/advisories/RUSTSEC-2019-0013.html
