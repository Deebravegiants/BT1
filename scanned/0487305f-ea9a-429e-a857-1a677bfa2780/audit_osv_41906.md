# [H] netfilter: bridge: eb_tables: close module init race

## Summary
Severity: High
Advisory: CVE-2026-64076
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64076
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: bridge: eb_tables: close module init race

sashiko reports for unrelated patch:
 Does the core ebtables initialization in ebtables.c suffer from a similar race?
 Once nf_register_sockopt() completes, the sockopts are exposed globally.

sockopt has to be registered last, just like in ip/ip6/arptables.

## References
- https://git.kernel.org/stable/c/02d999dc69b3918dba2414932b5d95f1f75c76cb
- https://git.kernel.org/stable/c/27414ff1b287ea9a2a11675149ec28e05539f3cc
- https://git.kernel.org/stable/c/c647e2a21bbbaceda6cdb8a44a56f44d231dc4b4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64076.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64076
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
