# [C] netfilter: nft_inner: release local_lock before re-enabling softirqs

## Summary
Severity: Critical
Advisory: CVE-2026-64150
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64150
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nft_inner: release local_lock before re-enabling softirqs

Quoting sashiko:
 In the error path, local_bh_enable() is called before
 local_unlock_nested_bh().

## References
- https://git.kernel.org/stable/c/6fecd39c6401134b58505bc4eb1adc8a0e2fe992
- https://git.kernel.org/stable/c/a6cb3ff979855f7f0ee9450a947fe8f96c2ba37a
- https://git.kernel.org/stable/c/df19b6af171695a1352314597c9a4311d48d5171
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64150.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64150
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
