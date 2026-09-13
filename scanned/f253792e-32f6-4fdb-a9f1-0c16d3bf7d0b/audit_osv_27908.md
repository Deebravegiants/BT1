# [H] cxl/pci: Skip to handle RAS errors if CXL.mem device is detached

## Summary
Severity: High
Advisory: CVE-2024-26762
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26762
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.7.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

cxl/pci: Skip to handle RAS errors if CXL.mem device is detached

The PCI AER model is an awkward fit for CXL error handling. While the
expectation is that a PCI device can escalate to link reset to recover
from an AER event, the same reset on CXL amounts to a surprise memory
hotplug of massive amounts of memory.

At present, the CXL error handler attempts some optimistic error
handling to unbind the device from the cxl_mem driver after reaping some
RAS register values. This results in a "hopeful" attempt to unplug the
memory, but there is no guarantee that will succeed.

A subsequent AER notification after the memdev unbind event can no
longer assume the registers are mapped. Check for memdev bind before
reaping status register values to avoid crashes of the form:

 BUG: unable to handle page fault for address: ffa00000195e9100
 #PF: supervisor read access in kernel mode
 #PF: error_code(0x0000) - not-present page
 [...]
 RIP: 0010:__cxl_handle_ras+0x30/0x110 [cxl_core]
 [...]
 Call Trace:
  <TASK>
  ? __die+0x24/0x70
  ? page_fault_oops+0x82/0x160
  ? kernelmode_fixup_or_oops+0x84/0x110
  ? exc_page_fault+0x113/0x170
  ? asm_exc_page_fault+0x26/0x30
  ? __pfx_dpc_reset_link+0x10/0x10
  ? __cxl_handle_ras+0x30/0x110 [cxl_core]
  ? find_cxl_port+0x59/0x80 [cxl_core]
  cxl_handle_rp_ras+0xbc/0xd0 [cxl_core]
  cxl_error_detected+0x6c/0xf0 [cxl_core]
  report_error_detected+0xc7/0x1c0
  pci_walk_bus+0x73/0x90
  pcie_do_recovery+0x23f/0x330

Longer term, the unbind and PCI_ERS_RESULT_DISCONNECT behavior might
need to be replaced with a new PCI_ERS_RESULT_PANIC.

## References
- https://git.kernel.org/stable/c/21e5e84f3f63fdf44e49642a6e45cd895e921a84
- https://git.kernel.org/stable/c/eef5c7b28dbecd6b141987a96db6c54e49828102
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26762.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26762
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
