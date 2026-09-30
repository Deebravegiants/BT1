# [H] regulator: core: regulator_lock_two() should test for EDEADLK not EDEADLOCK

## Summary
Severity: High
Advisory: CVE-2026-72314
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72314
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.4.0 <6.12.97, >=6.7.0 <6.18.40, >=6.13.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

regulator: core: regulator_lock_two() should test for EDEADLK not EDEADLOCK

Compare against -EDEADLK, which is what ww_mutex_lock() actually
returns and what every other deadlock check in this file already uses.

Function regulator_lock_two() acquires two regulators via
regulator_lock_nested() -> ww_mutex_lock().  On contention,
ww_mutex_lock() returns -EDEADLK, which is the caller's signal to drop
the lock it holds and retry the acquisition in the canonical order.

However, regulator_lock_two() tests the return value against -EDEADLOCK
rather than -EDEADLK.  On most architectures, EDEADLK and EDEADLOCK are
the same value, so the comparison happens to be correct and the bug is
invisible.  But on MIPS, SPARC, and PowerPC, those two errors have
different values.  The test is wrong: a genuine -EDEADLK backoff no
longer matches -EDEADLOCK, so instead of unlocking and retrying, the
code falls into WARN_ON(ret) and returns with only one of the two
regulators locked.

In practice, this is a bug only on MIPS, because the regulator core is
not built or used on the other two platforms.

In general, EDEADLK is preferred over EDEADLOCK for new code.

## References
- https://git.kernel.org/stable/c/0c305eac40470a224671858a215963b070f9b2a9
- https://git.kernel.org/stable/c/153d1b8b5bc30847eb70ad535f62f289aa9217e6
- https://git.kernel.org/stable/c/29a7953e9adea6c7f9e64947745b79158e7cea7f
- https://git.kernel.org/stable/c/346e2d666a29ae7233c56b356a0487eb1d42589b
- https://git.kernel.org/stable/c/8e39aa63798ea0a797fd9341419f12ef91df3238
- https://git.kernel.org/stable/c/d38f8bd771c4999b797d7074b348cf201414bd34
- https://git.kernel.org/stable/c/dc804f390fddd9c389edf0976356942e16878d8f
- https://git.kernel.org/stable/c/e2063307ea3b6da74585129ba7b588e8243e2ef0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72314.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72314
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
