# [H] octeon_ep: cancel queued works in probe error path

## Summary
Severity: High
Advisory: CVE-2023-53638
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-07
Source: https://osv.dev/vulnerability/CVE-2023-53638
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.4.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

octeon_ep: cancel queued works in probe error path

If it fails to get the devices's MAC address, octep_probe exits while
leaving the delayed work intr_poll_task queued. When the work later
runs, it's a use after free.

Move the cancelation of intr_poll_task from octep_remove into
octep_device_cleanup. This does not change anything in the octep_remove
flow, but octep_device_cleanup is called also in the octep_probe error
path, where the cancelation is needed.

Note that the cancelation of ctrl_mbox_task has to follow
intr_poll_task's, because the ctrl_mbox_task may be queued by
intr_poll_task.

## References
- https://git.kernel.org/stable/c/62312e2f6466b5f0a120542a38b410d88a34ed00
- https://git.kernel.org/stable/c/758c91078165ae641b698750a72eafe7968b3756
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53638.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53638
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
