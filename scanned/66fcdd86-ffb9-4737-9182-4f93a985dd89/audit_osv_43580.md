# [H] wifi: rtw88: fix wrong pci_get_drvdata type in AER handlers

## Summary
Severity: High
Advisory: CVE-2026-74412
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74412
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: rtw88: fix wrong pci_get_drvdata type in AER handlers

rtw88 stores an ieee80211_hw pointer via pci_set_drvdata() at probe
time, but io_error_detected() and io_resume() retrieve it as a
net_device pointer.  This causes netif_device_detach/attach to
operate on an ieee80211_hw struct, reading and writing at wrong
offsets.

Use ieee80211_stop_queues/wake_queues instead, consistent with
every other queue stop/start path in the driver.

## References
- https://git.kernel.org/stable/c/1ef3d1338d94ec41f58fbfb6ba7742a27ea61d89
- https://git.kernel.org/stable/c/706183dbef4a79d120d4e928f693bea50df496f8
- https://git.kernel.org/stable/c/d7920797f721f944861f3c48ffb2b73f84b631fe
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74412.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74412
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
