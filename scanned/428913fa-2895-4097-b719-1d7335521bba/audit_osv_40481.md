# [C] ocfs2/dlm: fix off-by-one in dlm_match_regions() region comparison

## Summary
Severity: Critical
Advisory: CVE-2026-53309
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-53309
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.37 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ocfs2/dlm: fix off-by-one in dlm_match_regions() region comparison

The local-vs-remote region comparison loop uses '<=' instead of '<',
causing it to read one entry past the valid range of qr_regions.  The
other loops in the same function correctly use '<'.

Fix the loop condition to use '<' for consistency and correctness.

## References
- https://git.kernel.org/stable/c/01b61e8dda9b0fdb0d4cda43de25f4e390554d7b
- https://git.kernel.org/stable/c/1fb7f356547d9688822315cd2b205ff0bd5429b4
- https://git.kernel.org/stable/c/2a0673836f019e7c032acbf48d022d5ccf02a845
- https://git.kernel.org/stable/c/426cd8eedac89b86148d4478990eeef16e8a2520
- https://git.kernel.org/stable/c/760ab35040aca8399021fdb9ff1db1089feb7194
- https://git.kernel.org/stable/c/819d8ebad3200a53de99bd7e297bc428e41ced54
- https://git.kernel.org/stable/c/c60a2710b73838d250cda57344c049b89abc5d52
- https://git.kernel.org/stable/c/d5403ae28085761d58b555645bc7d5feadb10073
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53309.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53309
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
