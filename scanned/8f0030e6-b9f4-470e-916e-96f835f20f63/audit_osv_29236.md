# [H] mmc: davinci_mmc: Prevent transmitted data size from exceeding sgm's length

## Summary
Severity: High
Advisory: CVE-2024-41026
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41026
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.9.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

mmc: davinci_mmc: Prevent transmitted data size from exceeding sgm's length

No check is done on the size of the data to be transmiited. This causes
a kernel panic when this size exceeds the sg_miter's length.

Limit the number of transmitted bytes to sgm->length.

## References
- https://git.kernel.org/stable/c/16198eef11c1929374381d7f6271b4bf6aa44615
- https://git.kernel.org/stable/c/c561c4ecce712f94b442db5960e281f13b28df2e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41026.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41026
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
