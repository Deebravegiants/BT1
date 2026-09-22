# [M] CVE-2021-47439

## Summary
Severity: Medium
Advisory: CVE-2021-47439
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47439
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: dsa: microchip: Added the condition for scheduling ksz_mib_read_work

When the ksz module is installed and removed using rmmod, kernel crashes
with null pointer dereferrence error. During rmmod, ksz_switch_remove
function tries to cancel the mib_read_workqueue using
cancel_delayed_work_sync routine and unregister switch from dsa.

During dsa_unregister_switch it calls ksz_mac_link_down, which in turn
reschedules the workqueue since mib_interval is non-zero.
Due to which queue executed after mib_interval and it tries to access
dp->slave. But the slave is unregistered in the ksz_switch_remove
function. Hence kernel crashes.

To avoid this crash, before canceling the workqueue, resetted the
mib_interval to 0.

v1 -> v2:
-Removed the if condition in ksz_mib_read_work

## References
- https://git.kernel.org/stable/c/f2e1de075018cf71bcd7d628e9f759cb8540b0c3
- https://git.kernel.org/stable/c/383239a33cf29ebee9ce0d4e0e5c900b77a16148
- https://git.kernel.org/stable/c/ef1100ef20f29aec4e62abeccdb5bdbebba1e378
