# [H] net: bridge: vlan: fix memory leak in __allowed_ingress

## Summary
Severity: High
Advisory: CVE-2022-48748
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-20
Source: https://osv.dev/vulnerability/CVE-2022-48748
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.96, >=5.11.0 <5.15.19, >=5.16.0 <5.16.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: bridge: vlan: fix memory leak in __allowed_ingress

When using per-vlan state, if vlan snooping and stats are disabled,
untagged or priority-tagged ingress frame will go to check pvid state.
If the port state is forwarding and the pvid state is not
learning/forwarding, untagged or priority-tagged frame will be dropped
but skb memory is not freed.
Should free skb when __allowed_ingress returns false.

## References
- https://git.kernel.org/stable/c/14be8d448fca6fe7b2a413831eedd55aef6c6511
- https://git.kernel.org/stable/c/446ff1fc37c74093e81db40811a07b5a19f1d797
- https://git.kernel.org/stable/c/c5e216e880fa6f2cd9d4a6541269377657163098
- https://git.kernel.org/stable/c/fd20d9738395cf8e27d0a17eba34169699fccdff
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48748.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48748
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
