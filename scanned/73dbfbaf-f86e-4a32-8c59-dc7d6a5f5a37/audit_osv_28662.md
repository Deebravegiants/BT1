# [C] smb: client: fix potential UAF in smb2_is_network_name_deleted()

## Summary
Severity: Critical
Advisory: CVE-2024-35862
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35862
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <6.1.85, >=6.2.0 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix potential UAF in smb2_is_network_name_deleted()

Skip sessions that are being teared down (status == SES_EXITING) to
avoid UAF.

## References
- https://git.kernel.org/stable/c/63981561ffd2d4987807df4126f96a11e18b0c1d
- https://git.kernel.org/stable/c/aa582b33f94453fdeaff1e7d0aa252c505975e01
- https://git.kernel.org/stable/c/d919b6ea15ffa56fbafef4a1d92f47aeda9af645
- https://git.kernel.org/stable/c/f9414004798d9742c1af23a1d839fe6a9503751c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35862.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35862
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
