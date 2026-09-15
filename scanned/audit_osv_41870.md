# [H] gpio: aggregator: fix a potential use-after-free

## Summary
Severity: High
Advisory: CVE-2026-64023
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64023
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

gpio: aggregator: fix a potential use-after-free

On error we free aggr->lookups->dev_id before removing the entry from
the lookup table. If a concurrent thread calls gpiod_find() before we
remove the entry, it could iterate over the list and call
gpiod_match_lookup_table() which unconditionally dereferences dev_id
when calling strcmp(). Reverse the order of cleanup.

## References
- https://git.kernel.org/stable/c/30c073cab97afb31901f94de9605177b6b84367e
- https://git.kernel.org/stable/c/7ac4183a41ba048af89eddd82fe8be64619d0871
- https://git.kernel.org/stable/c/ea28b286649b70618e9dd3e895812417a7712a11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64023.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64023
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
