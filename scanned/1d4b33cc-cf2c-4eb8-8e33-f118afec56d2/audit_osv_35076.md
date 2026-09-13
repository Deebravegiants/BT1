# [H] ice: fix PTP cleanup on driver removal in error path

## Summary
Severity: High
Advisory: CVE-2025-68215
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68215
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.60, >=6.13.0 <6.17.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ice: fix PTP cleanup on driver removal in error path

Improve the cleanup on releasing PTP resources in error path.
The error case might happen either at the driver probe and PTP
feature initialization or on PTP restart (errors in reset handling, NVM
update etc). In both cases, calls to PF PTP cleanup (ice_ptp_cleanup_pf
function) and 'ps_lock' mutex deinitialization were missed.
Additionally, ptp clock was not unregistered in the latter case.

Keep PTP state as 'uninitialized' on init to distinguish between error
scenarios and to avoid resource release duplication at driver removal.

The consequence of missing ice_ptp_cleanup_pf call is the following call
trace dumped when ice_adapter object is freed (port list is not empty,
as it is required at this stage):

[  T93022] ------------[ cut here ]------------
[  T93022] WARNING: CPU: 10 PID: 93022 at
ice/ice_adapter.c:67 ice_adapter_put+0xef/0x100 [ice]
...
[  T93022] RIP: 0010:ice_adapter_put+0xef/0x100 [ice]
...
[  T93022] Call Trace:
[  T93022]  <TASK>
[  T93022]  ? ice_adapter_put+0xef/0x100 [ice
33d2647ad4f6d866d41eefff1806df37c68aef0c]
[  T93022]  ? __warn.cold+0xb0/0x10e
[  T93022]  ? ice_adapter_put+0xef/0x100 [ice
33d2647ad4f6d866d41eefff1806df37c68aef0c]
[  T93022]  ? report_bug+0xd8/0x150
[  T93022]  ? handle_bug+0xe9/0x110
[  T93022]  ? exc_invalid_op+0x17/0x70
[  T93022]  ? asm_exc_invalid_op+0x1a/0x20
[  T93022]  ? ice_adapter_put+0xef/0x100 [ice
33d2647ad4f6d866d41eefff1806df37c68aef0c]
[  T93022]  pci_device_remove+0x42/0xb0
[  T93022]  device_release_driver_internal+0x19f/0x200
[  T93022]  driver_detach+0x48/0x90
[  T93022]  bus_remove_driver+0x70/0xf0
[  T93022]  pci_unregister_driver+0x42/0xb0
[  T93022]  ice_module_exit+0x10/0xdb0 [ice
33d2647ad4f6d866d41eefff1806df37c68aef0c]
...
[  T93022] ---[ end trace 0000000000000000 ]---
[  T93022] ice: module unloaded

## References
- https://git.kernel.org/stable/c/23a5b9b12de9dcd15ebae4f1abc8814ec1c51ab0
- https://git.kernel.org/stable/c/765236f2c4fbba7650436b71a0e350500e9ec15f
- https://git.kernel.org/stable/c/f5eb91f876ebecbcd90f9edcaea98dcb354603b3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68215.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68215
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
