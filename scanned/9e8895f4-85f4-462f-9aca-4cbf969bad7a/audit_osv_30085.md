# [H] afs: Fix the setting of the server responding flag

## Summary
Severity: High
Advisory: CVE-2024-49999
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49999
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

afs: Fix the setting of the server responding flag

In afs_wait_for_operation(), we set transcribe the call responded flag to
the server record that we used after doing the fileserver iteration loop -
but it's possible to exit the loop having had a response from the server
that we've discarded (e.g. it returned an abort or we started receiving
data, but the call didn't complete).

This means that op->server might be NULL, but we don't check that before
attempting to set the server flag.

## References
- https://git.kernel.org/stable/c/3d51ab44123f35dd1d646d99a15ebef10f55e263
- https://git.kernel.org/stable/c/97c953572d98080c5f1486155350bb688041747a
- https://git.kernel.org/stable/c/ff98751bae40faed1ba9c6a7287e84430f7dec64
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49999.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49999
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
