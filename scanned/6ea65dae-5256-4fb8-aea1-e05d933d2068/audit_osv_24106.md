# [H] netfilter: nf_tables: do not allow CHAIN_ID to refer to another table

## Summary
Severity: High
Advisory: CVE-2022-50212
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-50212
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.137, >=5.11.0 <5.15.61, >=5.16.0 <5.18.18, >=5.19.0 <5.19.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: do not allow CHAIN_ID to refer to another table

When doing lookups for chains on the same batch by using its ID, a chain
from a different table can be used. If a rule is added to a table but
refers to a chain in a different table, it will be linked to the chain in
table2, but would have expressions referring to objects in table1.

Then, when table1 is removed, the rule will not be removed as its linked to
a chain in table2. When expressions in the rule are processed or removed,
that will lead to a use-after-free.

When looking for chains by ID, use the table that was used for the lookup
by name, and only return chains belonging to that same table.

## References
- https://git.kernel.org/stable/c/0f49613a213d918af790c1276f79da741968de11
- https://git.kernel.org/stable/c/58e863f64ee3d0879297e5e53b646e4b91e59620
- https://git.kernel.org/stable/c/91501513016903077f91033fa5d2aa26cac399b2
- https://git.kernel.org/stable/c/95f466d22364a33d183509629d0879885b4f547e
- https://git.kernel.org/stable/c/9e7dcb88ec8e85e4a8ad0ea494ea2f90f32d2583
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50212.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50212
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
