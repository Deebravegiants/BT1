# [H] wifi: ath12k: do WoW offloads only on primary link

## Summary
Severity: High
Advisory: CVE-2026-46271
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-03
Source: https://osv.dev/vulnerability/CVE-2026-46271
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath12k: do WoW offloads only on primary link

In case of multi-link connection, WCN7850 firmware crashes due to WoW
offloads enabled on both primary and secondary links.

Change to do it only on primary link to fix it.

Tested-on: WCN7850 hw2.0 PCI WLAN.HMT.1.1.c5-00284-QCAHMTSWPL_V1.0_V2.0_SILICONZ-1

## References
- https://git.kernel.org/stable/c/7379837c3f9efa576dc2d716ebfaa3a113b3112f
- https://git.kernel.org/stable/c/e042da1085d9f1686c58a4378d5840f52a36598e
- https://git.kernel.org/stable/c/e62102ac9b773bdb08475aa9ca24dea61ae98708
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46271.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46271
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
