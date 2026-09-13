# [H] ice: add NULL check in eswitch lag check

## Summary
Severity: High
Advisory: CVE-2025-38526
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-08-16
Source: https://osv.dev/vulnerability/CVE-2025-38526
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.100, >=6.7.0 <6.12.40, >=6.13.0 <6.15.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ice: add NULL check in eswitch lag check

The function ice_lag_is_switchdev_running() is being called from outside of
the LAG event handler code.  This results in the lag->upper_netdev being
NULL sometimes.  To avoid a NULL-pointer dereference, there needs to be a
check before it is dereferenced.

## References
- https://git.kernel.org/stable/c/245917d3c5ed7c6ae720302b64eac5c6f0c85177
- https://git.kernel.org/stable/c/27591d926191e42b2332e4bad3bcd3a49def393b
- https://git.kernel.org/stable/c/3ce58b01ada408b372f15b7c992ed0519840e3cf
- https://git.kernel.org/stable/c/5a5d64f0eec82076b2c09fee2195d640cfbe3379
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38526.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38526
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
