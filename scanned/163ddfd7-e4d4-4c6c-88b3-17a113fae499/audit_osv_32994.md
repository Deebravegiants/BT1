# [H] ksmbd: limit repeated connections from clients with the same IP

## Summary
Severity: High
Advisory: CVE-2025-38501
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-08-16
Source: https://osv.dev/vulnerability/CVE-2025-38501
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.148, >=6.2.0 <6.6.102, >=6.7.0 <6.12.42, >=6.13.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: limit repeated connections from clients with the same IP

Repeated connections from clients with the same IP address may exhaust
the max connections and prevent other normal client connections.
This patch limit repeated connections from clients with the same IP.

## References
- http://www.openwall.com/lists/oss-security/2025/09/15/2
- https://git.kernel.org/stable/c/6073afe64510c302b7a0683a01e32c012eff715d
- https://git.kernel.org/stable/c/7e5d91d3e6c62a9755b36f29c35288f06c3cd86b
- https://git.kernel.org/stable/c/cb092fc3a62972a4aa47c9fe356c2c6a01cd840b
- https://git.kernel.org/stable/c/e6bb9193974059ddbb0ce7763fa3882bd60d4dc3
- https://git.kernel.org/stable/c/f1ce9258bcbce2491f9f71f7882b6eed0b33ec65
- https://git.kernel.org/stable/c/fa1c47af4ff641cf9197ecdb1f8240cbb30389c1
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38501.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38501
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
- https://github.com/keymaker-arch/KSMBDrain
