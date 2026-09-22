# [M] CVE-2023-1032

## Summary
Severity: Medium
Advisory: CVE-2023-1032
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:N/I:L/A:H)
Published: 2024-01-08
Source: https://osv.dev/vulnerability/CVE-2023-1032
Type: osv

## Details
The Linux kernel io_uring IORING_OP_SOCKET operation contained a double free in function __sys_socket_file() in file net/socket.c. This issue was introduced in da214a475f8bd1d3e9e7a19ddfeb4d1617551bab and fixed in 649c15c7691e9b13cbe9bf6c65c365350e056067.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1032.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-1032
- https://ubuntu.com/security/notices/USN-5977-1
- https://ubuntu.com/security/notices/USN-6024-1
- https://ubuntu.com/security/notices/USN-6033-1
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-1032
- https://www.openwall.com/lists/oss-security/2023/03/13/2
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
