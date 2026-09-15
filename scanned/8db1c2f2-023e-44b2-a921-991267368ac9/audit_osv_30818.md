# [H] Bluetooth: hci_core: Fix not checking skb length on hci_acldata_packet

## Summary
Severity: High
Advisory: CVE-2024-56590
Ecosystem: Linux
CVSS: 7.6 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56590
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_core: Fix not checking skb length on hci_acldata_packet

This fixes not checking if skb really contains an ACL header otherwise
the code may attempt to access some uninitilized/invalid memory past the
valid skb->data.

## References
- https://git.kernel.org/stable/c/219960a48771b35a3857a491b955c31d6c33d581
- https://git.kernel.org/stable/c/3fe288a8214e7dd784d1f9b7c9e448244d316b47
- https://git.kernel.org/stable/c/559b1c7ac2e212a23b3833d3baf3bd957771d02e
- https://git.kernel.org/stable/c/5e50d12cc6e95e1fde08f5db6992b616f714b0fb
- https://git.kernel.org/stable/c/93a6160dc198ffe5786da8bd8588cfd17f53b29a
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56590.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56590
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
