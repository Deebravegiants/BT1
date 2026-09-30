# [H] md/md-llbitmap: fix percpu_ref not resurrected on suspend timeout

## Summary
Severity: High
Advisory: CVE-2026-45955
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45955
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

md/md-llbitmap: fix percpu_ref not resurrected on suspend timeout

When llbitmap_suspend_timeout() times out waiting for percpu_ref to
become zero, it returns -ETIMEDOUT without resurrecting the percpu_ref.
The caller (md_llbitmap_daemon_fn) then continues to the next page
without calling llbitmap_resume(), leaving the percpu_ref in a killed
state permanently.

Fix this by resurrecting the percpu_ref before returning the error,
ensuring the page control structure remains usable for subsequent
operations.

## References
- https://git.kernel.org/stable/c/095417d6b669c2dec39a5842ccb94df915f97f54
- https://git.kernel.org/stable/c/2446d099350185caeed19ab2c0270451a97296fb
- https://git.kernel.org/stable/c/d119bd2e1643cc023210ff3c6f0657e4f914e71d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45955.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45955
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
