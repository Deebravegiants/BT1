# [H] eth: bnxt: avoid deadlock when canceling IRQ affinity notifier

## Summary
Severity: High
Advisory: CVE-2026-74745
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-74745
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

eth: bnxt: avoid deadlock when canceling IRQ affinity notifier

Unregistering IRQ affinity notifiers waits for the callback synchronously.
bnxt takes the netdev instance lock in the notifier (to restart the queue)
and cancels the work under the same lock. This may obviously deadlock.

Move the restart to the async service task. The queue restart isn't
super time sensitive. Store the new TPH tag, schedule the task.
Safely canceling the service task is already ironed out.

In bnxt_request_irq() the order of registering notifier, affinity and
initial TPH programming has to be inverted. I think it was racy
previously since user may trigger an update as soon as notifier
is installed.

There's a small known gap - if pcie_tph_get_cpu_st() fails at init
and the target tag is 0 we may miss programming the entry.
This does not seem worth fixing, the code has skip-on-failure
all over the place, anyway.

## References
- https://git.kernel.org/stable/c/51e96fa31f7e7eac2cba8f854e24d36600cc040b
- https://git.kernel.org/stable/c/8b1118fc5a5d2cdc21cc07b5106921ad4f77c544
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74745.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74745
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
