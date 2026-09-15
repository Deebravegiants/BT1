# [H] media: uvcvideo: Fix OOB read

## Summary
Severity: High
Advisory: CVE-2023-52565
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-03-02
Source: https://osv.dev/vulnerability/CVE-2023-52565
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.56, >=6.2.0 <6.5.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: uvcvideo: Fix OOB read

If the index provided by the user is bigger than the mask size, we might do
an out of bound read.

## References
- https://git.kernel.org/stable/c/09635bf4cdd4adf2160198a6041bcc7ca46c0558
- https://git.kernel.org/stable/c/41ebaa5e0eebea4c3bac96b72f9f8ae0d77c0bdb
- https://git.kernel.org/stable/c/8bcf70d787f7d53a3b85ad394f926cfef3eed023
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52565.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52565
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
