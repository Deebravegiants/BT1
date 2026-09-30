# [H] net: hns3: make sure ptp clock is unregister and freed if hclge_ptp_get_cycle returns an error

## Summary
Severity: High
Advisory: CVE-2025-21924
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21924
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.179, >=5.16.0 <6.1.131, >=6.2.0 <6.6.83, >=6.7.0 <6.12.19, >=6.13.0 <6.13.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: hns3: make sure ptp clock is unregister and freed if hclge_ptp_get_cycle returns an error

During the initialization of ptp, hclge_ptp_get_cycle might return an error
and returned directly without unregister clock and free it. To avoid that,
call hclge_ptp_destroy_clock to unregist and free clock if
hclge_ptp_get_cycle failed.

## References
- https://git.kernel.org/stable/c/21dba813d9821687a7f9aff576798ba21a859a32
- https://git.kernel.org/stable/c/2c04e507f3a5c5dc6e2b9ab37d8cdedee1ef1a37
- https://git.kernel.org/stable/c/33244e98aa9503585e585335fe2ceb4492630949
- https://git.kernel.org/stable/c/9cfc43c0e6e6a31122b4008d763a2960c206aa2d
- https://git.kernel.org/stable/c/b7365eab39831487a84e63a9638209b68dc54008
- https://git.kernel.org/stable/c/b7d8d4529984e2d4a72a6d552fb886233e8e83cb
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21924.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21924
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
