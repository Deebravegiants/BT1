# [H] CVE-2022-3977

## Summary
Severity: High
Advisory: CVE-2022-3977
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-12
Source: https://osv.dev/vulnerability/CVE-2022-3977
Type: osv

## Details
A use-after-free flaw was found in the Linux kernel MCTP (Management Component Transport Protocol) functionality. This issue occurs when a user simultaneously calls DROPTAG ioctl and socket close happens, which could allow a local user to crash the system or potentially escalate their privileges on the system.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=3a732b46736cd8a29092e4b0b1a9ba83e672bf89
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3977.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3977
- https://security.netapp.com/advisory/ntap-20230223-0005/
