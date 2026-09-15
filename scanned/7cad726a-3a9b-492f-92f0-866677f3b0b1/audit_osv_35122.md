# [H] coresight: tmc: add the handle of the event to the path

## Summary
Severity: High
Advisory: CVE-2025-68370
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2025-68370
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.17.13, >=6.18.0 <6.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

coresight: tmc: add the handle of the event to the path

The handle is essential for retrieving the AUX_EVENT of each CPU and is
required in perf mode. It has been added to the coresight_path so that
dependent devices can access it from the path when needed.

The existing bug can be reproduced with:
perf record -e cs_etm//k -C 0-9 dd if=/dev/zero of=/dev/null

Showing an oops as follows:
Unable to handle kernel paging request at virtual address 000f6e84934ed19e

Call trace:
 tmc_etr_get_buffer+0x30/0x80 [coresight_tmc] (P)
 catu_enable_hw+0xbc/0x3d0 [coresight_catu]
 catu_enable+0x70/0xe0 [coresight_catu]
 coresight_enable_path+0xb0/0x258 [coresight]

## References
- https://git.kernel.org/stable/c/aaa5abcc9d44d2c8484f779ab46d242d774cabcb
- https://git.kernel.org/stable/c/d0c9effd82f2c19b92acd07d357fac5f392d549a
- https://git.kernel.org/stable/c/faa8f38f7ccb344ace2c1f364efc70e3a12d32f3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68370.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68370
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
