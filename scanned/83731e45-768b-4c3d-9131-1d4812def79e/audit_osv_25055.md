# [M] CVE-2023-3022

## Summary
Severity: Medium
Advisory: CVE-2023-3022
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-06-19
Source: https://osv.dev/vulnerability/CVE-2023-3022
Type: osv

## Details
A flaw was found in the IPv6 module of the Linux kernel. The arg.result was not used consistently in fib6_rule_lookup, sometimes holding rt6_info and other times fib6_info. This was not accounted for in other parts of the code where rt6_info was expected unconditionally, potentially leading to a kernel panic in fib6_rule_suppress.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3022.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3022
- https://bugzilla.redhat.com/show_bug.cgi?id=2211440
- https://github.com/torvalds/linux/commit/a65120bae4b7
