# [H] ASoC: SOF: ipc4-mtrace: prevent underflow in sof_ipc4_priority_mask_dfs_write()

## Summary
Severity: High
Advisory: CVE-2023-52987
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-52987
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: SOF: ipc4-mtrace: prevent underflow in sof_ipc4_priority_mask_dfs_write()

The "id" comes from the user.  Change the type to unsigned to prevent
an array underflow.

## References
- https://git.kernel.org/stable/c/d52f34784e4e2f6e77671a9f104d8a69a3b5d24c
- https://git.kernel.org/stable/c/ea57680af47587397f5005d7758022441ed66d54
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52987.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52987
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
