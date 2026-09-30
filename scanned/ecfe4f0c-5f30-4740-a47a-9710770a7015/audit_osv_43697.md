# [H] ima: Instantiate file_truncate and path_truncate hooks

## Summary
Severity: High
Advisory: CVE-2026-74592
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74592
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ima: Instantiate file_truncate and path_truncate hooks

Instantiate the file_truncate and path_truncate LSM hooks to reset the
action cache flags (IMA_DONE_MASK) as soon as truncation is requested,
so the file, based on policy, is re-collected, re-measured, re-audited,
and re-appraised on next access.

## References
- https://git.kernel.org/stable/c/0baed1fa2184c81e4baf76f445d3faa4b738c8f7
- https://git.kernel.org/stable/c/5f46705d96eb60587aa7035acfcbec977e08d620
- https://git.kernel.org/stable/c/b80bed5c871a80151351342c065579405ce77145
- https://git.kernel.org/stable/c/dd21c96a71e876c8df9ec546b885a2c5f47bbb05
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74592.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74592
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
