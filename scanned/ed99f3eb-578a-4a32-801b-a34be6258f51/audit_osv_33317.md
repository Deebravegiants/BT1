# [H] tcp_metrics: use dst_dev_net_rcu()

## Summary
Severity: High
Advisory: CVE-2025-40075
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-28
Source: https://osv.dev/vulnerability/CVE-2025-40075
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <6.12.63, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp_metrics: use dst_dev_net_rcu()

Replace three dst_dev() with a lockdep enabled helper.

## References
- https://git.kernel.org/stable/c/07613a95326ebad2d1b88d883cd72546025a4f3e
- https://git.kernel.org/stable/c/4b89397807eb04986427c4786d065e9442834ad4
- https://git.kernel.org/stable/c/50c127a69cd6285300931853b352a1918cfa180f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40075.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40075
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
