# [M] gve: guard XSK operations on the existence of queues

## Summary
Severity: Medium
Advisory: CVE-2024-57933
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-21
Source: https://osv.dev/vulnerability/CVE-2024-57933
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.70, >=6.7.0 <6.12.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

gve: guard XSK operations on the existence of queues

This patch predicates the enabling and disabling of XSK pools on the
existence of queues. As it stands, if the interface is down, disabling
or enabling XSK pools would result in a crash, as the RX queue pointer
would be NULL. XSK pool registration will occur as part of the next
interface up.

Similarly, xsk_wakeup needs be guarded against queues disappearing
while the function is executing, so a check against the
GVE_PRIV_FLAGS_NAPI_ENABLED flag is added to synchronize with the
disabling of the bit and the synchronize_net() in gve_turndown.

## References
- https://git.kernel.org/stable/c/40338d7987d810fcaa95c500b1068a52b08eec9b
- https://git.kernel.org/stable/c/771d66f2bd8c4dba1286a9163ab982cecd825718
- https://git.kernel.org/stable/c/8e8d7037c89437af12725f454e2eaf40e8166c0f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57933.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57933
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
