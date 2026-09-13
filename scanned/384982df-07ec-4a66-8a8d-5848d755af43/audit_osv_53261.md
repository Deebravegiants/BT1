# [H] CVE-2022-3526

## Summary
Severity: High
Advisory: CVE-2022-3526
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-16
Source: https://osv.dev/vulnerability/CVE-2022-3526
Type: osv

## Details
A vulnerability classified as problematic was found in Linux Kernel. This vulnerability affects the function macvlan_handle_frame of the file drivers/net/macvlan.c of the component skb. The manipulation leads to memory leak. The attack can be initiated remotely. It is recommended to apply a patch to fix this issue. The identifier of this vulnerability is VDB-211024.

## References
- https://vuldb.com/?id.211024
- https://git.kernel.org/pub/scm/linux/kernel/git/pabeni/net-next.git/commit/?id=e16b859872b87650bb55b12cca5a5fcdc49c1442
