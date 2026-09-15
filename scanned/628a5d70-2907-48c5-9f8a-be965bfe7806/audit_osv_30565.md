# [H] crypto: qat/qat_4xxx - fix off by one in uof_get_name()

## Summary
Severity: High
Advisory: CVE-2024-53162
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-12-24
Source: https://osv.dev/vulnerability/CVE-2024-53162
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: qat/qat_4xxx - fix off by one in uof_get_name()

The fw_objs[] array has "num_objs" elements so the > needs to be >= to
prevent an out of bounds read.

## References
- https://git.kernel.org/stable/c/05c9a7a5344425860202a8f3efea4d8ed2d10edb
- https://git.kernel.org/stable/c/475b5098043eef6e72751aadeab687992a5b63d1
- https://git.kernel.org/stable/c/700852528fc5295897d6089eea0656d67f9b9d88
- https://git.kernel.org/stable/c/e69d2845aaa080960f38761f78fd25aa856620c6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53162.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53162
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
