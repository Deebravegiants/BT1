# [M] nfc: fdp: Fix potential memory leak in fdp_nci_send()

## Summary
Severity: Medium
Advisory: CVE-2022-49924
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49924
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <5.10.154, >=5.11.0 <5.15.78, >=5.16.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfc: fdp: Fix potential memory leak in fdp_nci_send()

fdp_nci_send() will call fdp_nci_i2c_write that will not free skb in
the function. As a result, when fdp_nci_i2c_write() finished, the skb
will memleak. fdp_nci_send() should free skb after fdp_nci_i2c_write()
finished.

## References
- https://git.kernel.org/stable/c/1a7a898f8f7b56c0eaa2baf67a0c96235a30bc29
- https://git.kernel.org/stable/c/44bc1868a4f542502ea2221fe5ad88ca66d1c6b6
- https://git.kernel.org/stable/c/8e4aae6b8ca76afb1fb64dcb24be44ba814e7f8a
- https://git.kernel.org/stable/c/e8c11ee2d07f7c4dfa2ac0ea8efc4f627e58ea57
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49924.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49924
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
