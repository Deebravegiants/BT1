# [C] ksmbd: add free_transport ops in ksmbd connection

## Summary
Severity: Critical
Advisory: CVE-2025-38325
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-38325
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: add free_transport ops in ksmbd connection

free_transport function for tcp connection can be called from smbdirect.
It will cause kernel oops. This patch add free_transport ops in ksmbd
connection, and add each free_transports for tcp and smbdirect.

## References
- https://git.kernel.org/stable/c/3890da762a66191c440b0bd6e3ee45501edbb0c1
- https://git.kernel.org/stable/c/3f3aae77280aad9f5acc6709c596148966f765c7
- https://git.kernel.org/stable/c/52f5a52dc17a4a7b4363ac03fe2c4ef26f020dc6
- https://git.kernel.org/stable/c/a89f5fae998bdc4d0505306f93844c9ae059d50c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38325.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38325
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
