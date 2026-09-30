# [H] smb: client: fix potential UAF in cifs_stats_proc_show()

## Summary
Severity: High
Advisory: CVE-2024-35867
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35867
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <5.10.237, >=5.11.0 <5.15.181, >=5.16.0 <6.1.85, >=6.2.0 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix potential UAF in cifs_stats_proc_show()

Skip sessions that are being teared down (status == SES_EXITING) to
avoid UAF.

## References
- http://www.openwall.com/lists/oss-security/2024/05/29/2
- http://www.openwall.com/lists/oss-security/2024/05/30/1
- http://www.openwall.com/lists/oss-security/2024/05/30/2
- https://git.kernel.org/stable/c/0865ffefea197b437ba78b5dd8d8e256253efd65
- https://git.kernel.org/stable/c/16b7d785775eb03929766819415055e367398f49
- https://git.kernel.org/stable/c/1e12f0d5c66f07c934041621351973a116fa13c7
- https://git.kernel.org/stable/c/838ec01ea8d3deb5d123e8ed9022e8162dc3f503
- https://git.kernel.org/stable/c/bb6570085826291dc392005f9fec16ea5da3c8ad
- https://git.kernel.org/stable/c/c3cf8b74c57924c0985e49a1fdf02d3395111f39
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35867.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35867
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
