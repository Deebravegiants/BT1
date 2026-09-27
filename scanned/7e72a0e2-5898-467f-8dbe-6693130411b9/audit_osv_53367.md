# [M] CVE-2022-4129

## Summary
Severity: Medium
Advisory: CVE-2022-4129
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-11-28
Source: https://osv.dev/vulnerability/CVE-2022-4129
Type: osv

## Details
A flaw was found in the Linux kernel's Layer 2 Tunneling Protocol (L2TP). A missing lock when clearing sk_user_data can lead to a race condition and NULL pointer dereference. A local user could use this flaw to potentially crash the system causing a denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7X5SPXMXXFANDASPCKER2JIQO2F3UHCP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AM5KFIE6JNZXHBA5A2KYDZAT3MEX2B67/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JOKXNIM2R4FQCDRQV67UMAY6EBC72QFG/
- https://lore.kernel.org/all/20221114191619.124659-1-jakub%40cloudflare.com/t
- https://lore.kernel.org/netdev/20221121085426.21315-1-jakub%40cloudflare.com/t
