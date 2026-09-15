# [H] netfilter: ebtables: move to two-stage removal scheme

## Summary
Severity: High
Advisory: CVE-2026-64077
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64077
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: ebtables: move to two-stage removal scheme

Like previous patches for x_tables, follow same pattern in ebtables.
We can't reuse xt helpers: ebt_table struct layout is incompatible.

table->ops assignment is now done while still holding the ebt mutex
to make sure we never expose partially-filled table struct.

## References
- https://git.kernel.org/stable/c/739d5dac7b2da44a756aa4d758ee3f1ccf5a27f1
- https://git.kernel.org/stable/c/b7f0544d86d439cb946515d2ef6a0a75e8626710
- https://git.kernel.org/stable/c/ef395579a7631a06d61969fc712eb80402231b89
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64077.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64077
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
