# [H] rtw88: fix memory overrun and memory leak during hw_scan

## Summary
Severity: High
Advisory: CVE-2022-49231
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49231
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

rtw88: fix memory overrun and memory leak during hw_scan

Previously we allocated less memory than actual required, overwrite
to the buffer causes the mm module to complaint and raise access
violation faults. Along with potential memory leaks when returned
early. Fix these by passing the correct size and proper deinit flow.

## References
- https://git.kernel.org/stable/c/d95984b5580dcb8b1c0036577c52b609990a1dab
- https://git.kernel.org/stable/c/ec5da191bfcd5fd22b95459b623694f66c1cc10b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49231.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49231
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
