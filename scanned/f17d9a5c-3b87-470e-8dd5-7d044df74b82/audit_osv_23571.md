# [M] net: dsa: felix: fix possible NULL pointer dereference

## Summary
Severity: Medium
Advisory: CVE-2022-49141
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49141
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: dsa: felix: fix possible NULL pointer dereference

As the possible failure of the allocation, kzalloc() may return NULL
pointer.
Therefore, it should be better to check the 'sgi' in order to prevent
the dereference of NULL pointer.

## References
- https://git.kernel.org/stable/c/866b7a278cdb51eb158cd8513bc7438fc857804a
- https://git.kernel.org/stable/c/b7ff8b5e75d4e91ec8c62d621aac8dfb84c57aa9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49141.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49141
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
