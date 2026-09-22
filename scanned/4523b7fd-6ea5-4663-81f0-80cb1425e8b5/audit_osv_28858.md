# [H] usb: dwc3: Wait unconditionally after issuing EndXfer command

## Summary
Severity: High
Advisory: CVE-2024-36977
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-18
Source: https://osv.dev/vulnerability/CVE-2024-36977
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.92, >=6.2.0 <6.6.32, >=6.7.0 <6.8.11, >=6.9.0 <6.9.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: dwc3: Wait unconditionally after issuing EndXfer command

Currently all controller IP/revisions except DWC3_usb3 >= 310a
wait 1ms unconditionally for ENDXFER completion when IOC is not
set. This is because DWC_usb3 controller revisions >= 3.10a
supports GUCTL2[14: Rst_actbitlater] bit which allows polling
CMDACT bit to know whether ENDXFER command is completed.

Consider a case where an IN request was queued, and parallelly
soft_disconnect was called (due to ffs_epfile_release). This
eventually calls stop_active_transfer with IOC cleared, hence
send_gadget_ep_cmd() skips waiting for CMDACT cleared during
EndXfer. For DWC3 controllers with revisions >= 310a, we don't
forcefully wait for 1ms either, and we proceed by unmapping the
requests. If ENDXFER didn't complete by this time, it leads to
SMMU faults since the controller would still be accessing those
requests.

Fix this by ensuring ENDXFER completion by adding 1ms delay in
__dwc3_stop_active_transfer() unconditionally.

## References
- https://git.kernel.org/stable/c/1ba145f05b5c8f0b1a947a0633b5edff5dd1f1c5
- https://git.kernel.org/stable/c/1d26ba0944d398f88aaf997bda3544646cf21945
- https://git.kernel.org/stable/c/341eb08dbca9eae05308c442fbfab1813a44c97a
- https://git.kernel.org/stable/c/4a387e032909c6dc2b479452c5bbe9a252057925
- https://git.kernel.org/stable/c/ec96bcf5f96a7a5c556b0e881ac3e5c3924d542c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36977.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36977
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
