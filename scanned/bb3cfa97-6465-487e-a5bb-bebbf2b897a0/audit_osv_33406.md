# [H] io_uring: fix regbuf vector size truncation

## Summary
Severity: High
Advisory: CVE-2025-40291
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2025-40291
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring: fix regbuf vector size truncation

There is a report of io_estimate_bvec_size() truncating the calculated
number of segments that leads to corruption issues. Check it doesn't
overflow "int"s used later. Rough but simple, can be improved on top.

## References
- https://git.kernel.org/stable/c/146eb58629f45f8297e83d69e64d4eea4b28d972
- https://git.kernel.org/stable/c/826ce37a842633efe1bb763e4b13045d74060d72
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40291.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40291
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
