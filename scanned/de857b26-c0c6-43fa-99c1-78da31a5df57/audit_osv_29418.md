# [H] btrfs: fix extent map use-after-free when adding pages to compressed bio

## Summary
Severity: High
Advisory: CVE-2024-42314
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-42314
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.108, >=6.2.0 <6.6.44, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: fix extent map use-after-free when adding pages to compressed bio

At add_ra_bio_pages() we are accessing the extent map to calculate
'add_size' after we dropped our reference on the extent map, resulting
in a use-after-free. Fix this by computing 'add_size' before dropping our
extent map reference.

## References
- https://git.kernel.org/stable/c/8e7860543a94784d744c7ce34b78a2e11beefa5c
- https://git.kernel.org/stable/c/b7859ff398b6b656e1689daa860eb34837b4bb89
- https://git.kernel.org/stable/c/c1cc3326e27b0bd7a2806b40bc48e49afaf951e7
- https://git.kernel.org/stable/c/c205565e0f2f439f278a4a94ee97b67ef7b56ae8
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42314.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42314
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
