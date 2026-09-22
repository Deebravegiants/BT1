# [C] 9p/net: fix improper handling of bogus negative read/write replies

## Summary
Severity: Critical
Advisory: CVE-2025-37879
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-09
Source: https://osv.dev/vulnerability/CVE-2025-37879
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <6.1.136, >=6.2.0 <6.6.89, >=6.7.0 <6.12.26, >=6.13.0 <6.14.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

9p/net: fix improper handling of bogus negative read/write replies

In p9_client_write() and p9_client_read_once(), if the server
incorrectly replies with success but a negative write/read count then we
would consider written (negative) <= rsize (positive) because both
variables were signed.

Make variables unsigned to avoid this problem.

The reproducer linked below now fails with the following error instead
of a null pointer deref:
9pnet: bogus RWRITE count (4294967295 > 3)

## References
- https://git.kernel.org/stable/c/374e4cd75617c8c2552f562f39dd989583f5c330
- https://git.kernel.org/stable/c/468ff4a7c61fb811c596a7c44b6a5455e40fd12b
- https://git.kernel.org/stable/c/a68768e280b7d0c967ea509e791bb9b90adc94a5
- https://git.kernel.org/stable/c/c548f95688e2b5ae0e2ae43d53cf717156c7d034
- https://git.kernel.org/stable/c/d0259a856afca31d699b706ed5e2adf11086c73b
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37879.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37879
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
