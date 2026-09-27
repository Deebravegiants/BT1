# [H] media: rockchip: rkcif: fix off by one bugs

## Summary
Severity: High
Advisory: CVE-2026-52907
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-52907
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: rockchip: rkcif: fix off by one bugs

Change these comparisons from > vs >= to avoid accessing one element
beyond the end of the arrays.
While at it, use ARRAY_SIZE instead of the _MAX enum values.

[fix cosmetic issues]

## References
- https://git.kernel.org/stable/c/73e119036b3a799170ed89907b4273c07306d611
- https://git.kernel.org/stable/c/e4056b84af0fc18c84b4e5741df04ecd8ca17973
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52907.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52907
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
