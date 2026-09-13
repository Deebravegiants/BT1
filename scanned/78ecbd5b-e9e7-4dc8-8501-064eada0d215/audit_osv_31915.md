# [M] sched: address a potential NULL pointer dereference in the GRED scheduler.

## Summary
Severity: Medium
Advisory: CVE-2025-21980
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21980
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.132, >=6.2.0 <6.6.84, >=6.7.0 <6.12.20, >=6.13.0 <6.13.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

sched: address a potential NULL pointer dereference in the GRED scheduler.

If kzalloc in gred_init returns a NULL pointer, the code follows the
error handling path, invoking gred_destroy. This, in turn, calls
gred_offload, where memset could receive a NULL pointer as input,
potentially leading to a kernel crash.

When table->opt is NULL in gred_init(), gred_change_table_def()
is not called yet, so it is not necessary to call ->ndo_setup_tc()
in gred_offload().

## References
- https://git.kernel.org/stable/c/0f0a152957d64ce45b4c27c687e7d087e8f45079
- https://git.kernel.org/stable/c/115ef44a98220fddfab37a39a19370497cd718b9
- https://git.kernel.org/stable/c/5f996b4f80c2cef1f9c77275055e7fcba44c9199
- https://git.kernel.org/stable/c/68896dd50180b38ea552e49a6a00b685321e5769
- https://git.kernel.org/stable/c/d02c9acd68950a444acda18d514e2b41f846cb7f
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21980.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21980
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
