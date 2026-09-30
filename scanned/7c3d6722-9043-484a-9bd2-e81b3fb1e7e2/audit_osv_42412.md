# [H] drm/amdgpu: reject mapping a reserved doorbell to a new queue

## Summary
Severity: High
Advisory: CVE-2026-68103
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68103
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: reject mapping a reserved doorbell to a new queue

When creating an user-queue, the user space
provides a doorbell BO handle and an offset within
the bo to obtain a doorbell.

However current implementation using xa_store_irq()
to store a doorbell, which allows a later queue created
with the same BO and offset parameters to overwrite an
existing queue and doorbell mapping.

This can cause problems like misrouting fence IRQ
processing to a wrong queue, and mislead the cleanup
process of one queue erasing the mapping of another queue.

This commit fixes this issue by replacing xa_store_irq with
xa_insert_irq, which rejects mapping a reserved
doorbell to a newly created queue

(cherry picked from commit 6244eae22966350db52faf9c1369d3b2ffc5de4e)

## References
- https://git.kernel.org/stable/c/1050d258c7c56066d2dcaedf8d0ef66364062adc
- https://git.kernel.org/stable/c/a609b6278bf3cde17eeee6620091465521e4b02c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68103.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68103
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
