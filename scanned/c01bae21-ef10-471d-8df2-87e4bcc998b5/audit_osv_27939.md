# [C] cifs: fix underflow in parse_server_interfaces()

## Summary
Severity: Critical
Advisory: CVE-2024-26828
Ecosystem: Linux
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26828
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <6.1.79, >=6.2.0 <6.6.18, >=6.7.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: fix underflow in parse_server_interfaces()

In this loop, we step through the buffer and after each item we check
if the size_left is greater than the minimum size we need.  However,
the problem is that "bytes_left" is type ssize_t while sizeof() is type
size_t.  That means that because of type promotion, the comparison is
done as an unsigned and if we have negative bytes left the loop
continues instead of ending.

## References
- https://git.kernel.org/stable/c/7190353835b4a219abb70f90b06cdcae97f11512
- https://git.kernel.org/stable/c/cffe487026be13eaf37ea28b783d9638ab147204
- https://git.kernel.org/stable/c/df2af9fdbc4ddde18a3371c4ca1a86596e8be301
- https://git.kernel.org/stable/c/f7ff1c89fb6e9610d2b01c1821727729e6609308
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26828.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26828
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
