# [C] net: mana: Fix TOCTOU double-fetch of hwc_msg_id from DMA buffer

## Summary
Severity: Critical
Advisory: CVE-2026-64034
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64034
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: mana: Fix TOCTOU double-fetch of hwc_msg_id from DMA buffer

In mana_hwc_rx_event_handler(), resp->response.hwc_msg_id is read from
DMA-coherent memory and bounds-checked, then mana_hwc_handle_resp()
re-reads the same field from the same DMA buffer for test_bit() and
pointer arithmetic.

DMA-coherent memory is mapped uncacheable on x86 and is shared,
unencrypted, in Confidential VMs (SEV-SNP/TDX), so each load goes
directly to host-visible memory. A H/W can modify the value
between the check and the use, bypassing the bounds validation.

Fix this by reading hwc_msg_id exactly once using READ_ONCE() into a
stack-local variable in mana_hwc_rx_event_handler(), and passing the
validated value as a parameter to mana_hwc_handle_resp().

## References
- https://git.kernel.org/stable/c/09ec063d87c2dd3fa6f3561361a017bd882e9f37
- https://git.kernel.org/stable/c/35f0f0a2536a4d604b4dbad92c85c4a8fdebb870
- https://git.kernel.org/stable/c/3c4db56ccd13dd020fbf43afabaee74a40ec75e4
- https://git.kernel.org/stable/c/566f42fb67a7ebfed6650e407e5b72e6b3e83bf7
- https://git.kernel.org/stable/c/6180a06bbc99fd9114b8db4be6c4d46e40f046ef
- https://git.kernel.org/stable/c/70ad2dff8d052a85dfef15715b531f38a29108cf
- https://git.kernel.org/stable/c/a201c66edf2ebc6cfdc3813a889ba20fecebfae3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64034.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64034
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
