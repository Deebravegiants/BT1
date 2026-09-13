# [H] greybus: Fix use-after-free bug in gb_interface_release due to race condition.

## Summary
Severity: High
Advisory: CVE-2024-39495
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-39495
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.4.279, >=5.5.0 <5.10.221, >=5.11.0 <5.15.162, >=5.16.0 <6.1.95, >=6.2.0 <6.6.35, >=6.7.0 <6.9.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

greybus: Fix use-after-free bug in gb_interface_release due to race condition.

In gb_interface_create, &intf->mode_switch_completion is bound with
gb_interface_mode_switch_work. Then it will be started by
gb_interface_request_mode_switch. Here is the relevant code.
if (!queue_work(system_long_wq, &intf->mode_switch_work)) {
	...
}

If we call gb_interface_release to make cleanup, there may be an
unfinished work. This function will call kfree to free the object
"intf". However, if gb_interface_mode_switch_work is scheduled to
run after kfree, it may cause use-after-free error as
gb_interface_mode_switch_work will use the object "intf".
The possible execution flow that may lead to the issue is as follows:

CPU0                            CPU1

                            |   gb_interface_create
                            |   gb_interface_request_mode_switch
gb_interface_release        |
kfree(intf) (free)          |
                            |   gb_interface_mode_switch_work
                            |   mutex_lock(&intf->mutex) (use)

Fix it by canceling the work before kfree.

## References
- https://git.kernel.org/stable/c/03ea2b129344152157418929f06726989efc0445
- https://git.kernel.org/stable/c/0b8fba38bdfb848fac52e71270b2aa3538c996ea
- https://git.kernel.org/stable/c/2b6bb0b4abfd79b8698ee161bb73c0936a2aaf83
- https://git.kernel.org/stable/c/5c9c5d7f26acc2c669c1dcf57d1bb43ee99220ce
- https://git.kernel.org/stable/c/74cd0a421896b2e07eafe7da4275302bfecef201
- https://git.kernel.org/stable/c/9a733d69a4a59c2d08620e6589d823c24be773dc
- https://git.kernel.org/stable/c/fb071f5c75d4b1c177824de74ee75f9dd34123b9
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39495.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39495
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
