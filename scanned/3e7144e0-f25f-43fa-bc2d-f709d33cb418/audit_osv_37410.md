# [H] Bluetooth: MGMT: Fix dangling pointer on mgmt_add_adv_patterns_monitor_complete

## Summary
Severity: High
Advisory: CVE-2026-31511
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31511
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.80, >=6.13.0 <6.18.21, >=6.17.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: MGMT: Fix dangling pointer on mgmt_add_adv_patterns_monitor_complete

This fixes the condition checking so mgmt_pending_valid is executed
whenever status != -ECANCELED otherwise calling mgmt_pending_free(cmd)
would kfree(cmd) without unlinking it from the list first, leaving a
dangling pointer. Any subsequent list traversal (e.g.,
mgmt_pending_foreach during __mgmt_power_off, or another
mgmt_pending_valid call) would dereference freed memory.

## References
- https://git.kernel.org/stable/c/2074dfffad76981ca451cb7fc98703d04ac562fe
- https://git.kernel.org/stable/c/340666172cf747de58c283d2eef1f335f050538b
- https://git.kernel.org/stable/c/3a89c33deffb3cb7877a7ea2e50734cd12b064f2
- https://git.kernel.org/stable/c/5f5fa4cd35f707344f65ce9e225b6528691dbbaa
- https://git.kernel.org/stable/c/bafec9325d4de26b6c49db75b5d5172de652aae0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31511.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31511
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
