# [M] Bluetooth: hci_sync: fix memory leak in hci_update_adv_data()

## Summary
Severity: Medium
Advisory: CVE-2023-53017
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-53017
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_sync: fix memory leak in hci_update_adv_data()

When hci_cmd_sync_queue() failed in hci_update_adv_data(), inst_ptr is
not freed, which will cause memory leak, convert to use ERR_PTR/PTR_ERR
to pass the instance to callback so no memory needs to be allocated.

## References
- https://git.kernel.org/stable/c/1ed8b37cbaf14574c779064ef1372af62e8ba6aa
- https://git.kernel.org/stable/c/8ac6043bd3e5b58d30f50737aedc2e58e8087ad5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53017.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53017
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
