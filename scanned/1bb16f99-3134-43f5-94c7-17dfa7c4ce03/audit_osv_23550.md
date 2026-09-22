# [H] netfilter: conntrack: revisit gc autotuning

## Summary
Severity: High
Advisory: CVE-2022-49110
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49110
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.34, >=5.16.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: conntrack: revisit gc autotuning

as of commit 4608fdfc07e1
("netfilter: conntrack: collect all entries in one cycle")
conntrack gc was changed to run every 2 minutes.

On systems where conntrack hash table is set to large value, most evictions
happen from gc worker rather than the packet path due to hash table
distribution.

This causes netlink event overflows when events are collected.

This change collects average expiry of scanned entries and
reschedules to the average remaining value, within 1 to 60 second interval.

To avoid event overflows, reschedule after each bucket and add a
limit for both run time and number of evictions per run.

If more entries have to be evicted, reschedule and restart 1 jiffy
into the future.

## References
- https://git.kernel.org/stable/c/2cfadb761d3d0219412fd8150faea60c7e863833
- https://git.kernel.org/stable/c/58d52743ae85d28c9335c6034d6ce350b8689951
- https://git.kernel.org/stable/c/592e57591826f3d09c28d755a39ea8e9d13705ad
- https://git.kernel.org/stable/c/7cd361d5e6d986c0d4cafb9ceaa803359048ae15
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49110.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49110
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
