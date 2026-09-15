# [C] smb: client: fix potential UAF in cifs_signal_cifsd_for_reconnect()

## Summary
Severity: Critical
Advisory: CVE-2024-35861
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35861
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.85, >=6.2.0 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix potential UAF in cifs_signal_cifsd_for_reconnect()

Skip sessions that are being teared down (status == SES_EXITING) to
avoid UAF.

## References
- https://git.kernel.org/stable/c/2cfff21732132e363b4cc275d63ea98f1af726c1
- https://git.kernel.org/stable/c/7e8360ac8774e19b0b25f44fff84a105bb2417e4
- https://git.kernel.org/stable/c/e0e50401cc3921c9eaf1b0e667db174519ea939f
- https://git.kernel.org/stable/c/f9a96a7ad1e8d25dc6662bc7552e0752de74a20d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35861.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35861
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
