# [H] HID: intel-ish-hid: ipc: Fix potential use-after-free in work function

## Summary
Severity: High
Advisory: CVE-2023-53039
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-02
Source: https://osv.dev/vulnerability/CVE-2023-53039
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.15.105, >=5.16.0 <6.1.22, >=6.2.0 <6.2.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: intel-ish-hid: ipc: Fix potential use-after-free in work function

When a reset notify IPC message is received, the ISR schedules a work
function and passes the ISHTP device to it via a global pointer
ishtp_dev. If ish_probe() fails, the devm-managed device resources
including ishtp_dev are freed, but the work is not cancelled, causing a
use-after-free when the work function tries to access ishtp_dev. Use
devm_work_autocancel() instead, so that the work is automatically
cancelled if probe fails.

## References
- https://git.kernel.org/stable/c/0a594cb490ca6232671fc09e2dc1a0fc7ccbb0b5
- https://git.kernel.org/stable/c/8ae2f2b0a28416ed2f6d8478ac8b9f7862f36785
- https://git.kernel.org/stable/c/8c1d378b8c224fd50247625255f09fc01dcc5836
- https://git.kernel.org/stable/c/d3ce3afd9f791dd1b7daedfcf8c396b60af5dec0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53039.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53039
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
