# [H] media: dvb-core: add missing buffer index check

## Summary
Severity: High
Advisory: CVE-2024-50291
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50291
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: dvb-core: add missing buffer index check

dvb_vb2_expbuf() didn't check if the given buffer index was
for a valid buffer. Add this check.

## References
- https://git.kernel.org/stable/c/721c37af0355cc0b540909c57fd7930dc99c72d8
- https://git.kernel.org/stable/c/fa88dc7db176c79b50adb132a56120a1d4d9d18b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50291.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50291
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
