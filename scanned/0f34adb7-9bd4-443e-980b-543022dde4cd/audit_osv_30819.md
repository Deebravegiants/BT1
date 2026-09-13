# [H] Bluetooth: hci_conn: Use disable_delayed_work_sync

## Summary
Severity: High
Advisory: CVE-2024-56591
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56591
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.3.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_conn: Use disable_delayed_work_sync

This makes use of disable_delayed_work_sync instead
cancel_delayed_work_sync as it not only cancel the ongoing work but also
disables new submit which is disarable since the object holding the work
is about to be freed.

## References
- https://git.kernel.org/stable/c/2b0f2fc9ed62e73c95df1fa8ed2ba3dac54699df
- https://git.kernel.org/stable/c/c55a4c5a04bae40dcdc1e1c19d8eb79a06fb3397
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56591.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56591
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
