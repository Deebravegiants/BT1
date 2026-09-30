# [H] smb3: fix lock ordering potential deadlock in cifs_sync_mid_result

## Summary
Severity: High
Advisory: CVE-2024-35998
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-20
Source: https://osv.dev/vulnerability/CVE-2024-35998
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.90, >=6.2.0 <6.6.30, >=6.4.0 <6.8.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb3: fix lock ordering potential deadlock in cifs_sync_mid_result

Coverity spotted that the cifs_sync_mid_result function could deadlock

"Thread deadlock (ORDER_REVERSAL) lock_order: Calling spin_lock acquires
lock TCP_Server_Info.srv_lock while holding lock TCP_Server_Info.mid_lock"

Addresses-Coverity: 1590401 ("Thread deadlock (ORDER_REVERSAL)")

## References
- https://git.kernel.org/stable/c/699f8958dece132709c0bff6a9700999a2a63b75
- https://git.kernel.org/stable/c/8248224ab5b8ca7559b671917c224296a4d671fc
- https://git.kernel.org/stable/c/8861fd5180476f45f9e8853db154600469a0284f
- https://git.kernel.org/stable/c/c7a4bca289e50bb4b2650f845c41bb3e453f4c66
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35998.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35998
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
