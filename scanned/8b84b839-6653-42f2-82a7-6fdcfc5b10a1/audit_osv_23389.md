# [H] exfat: fix overflow for large capacity partition

## Summary
Severity: High
Advisory: CVE-2022-48665
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-04-28
Source: https://osv.dev/vulnerability/CVE-2022-48665
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <5.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

exfat: fix overflow for large capacity partition

Using int type for sector index, there will be overflow in a large
capacity partition.

For example, if storage with sector size of 512 bytes and partition
capacity is larger than 2TB, there will be overflow.

## References
- https://git.kernel.org/stable/c/17244f71765dfec39e84493993993e896c376d09
- https://git.kernel.org/stable/c/2e9ceb6728f1dc2fa4b5d08f37d88cbc49a20a62
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48665.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48665
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
