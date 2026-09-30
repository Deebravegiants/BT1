# [H] net/mlx5e: Fix use-after-free when reverting termination table

## Summary
Severity: High
Advisory: CVE-2022-49025
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2022-49025
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.4.226, >=5.5.0 <5.10.158, >=5.11.0 <5.15.82, >=5.16.0 <6.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5e: Fix use-after-free when reverting termination table

When having multiple dests with termination tables and second one
or afterwards fails the driver reverts usage of term tables but
doesn't reset the assignment in attr->dests[num_vport_dests].termtbl
which case a use-after-free when releasing the rule.
Fix by resetting the assignment of termtbl to null.

## References
- https://git.kernel.org/stable/c/0a2d73a77060c3cbdc6e801cd5d979d674cd404b
- https://git.kernel.org/stable/c/0d2f9d95d9fbe993f3c4bafb87d59897b0325aff
- https://git.kernel.org/stable/c/372eb550faa0757349040fd43f59483cbfdb2c0b
- https://git.kernel.org/stable/c/52c795af04441d76f565c4634f893e5b553df2ae
- https://git.kernel.org/stable/c/e6d2d26a49c3a9cd46b232975e45236304810904
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49025.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49025
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
