# [H] netfilter: nftables: exthdr: fix 4-byte stack OOB write

## Summary
Severity: High
Advisory: CVE-2023-52628
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-28
Source: https://osv.dev/vulnerability/CVE-2023-52628
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <4.19.316, >=4.20.0 <5.4.279, >=5.5.0 <5.10.198, >=5.11.0 <5.15.132, >=5.16.0 <6.1.54, >=6.2.0 <6.5.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nftables: exthdr: fix 4-byte stack OOB write

If priv->len is a multiple of 4, then dst[len / 4] can write past
the destination array which leads to stack corruption.

This construct is necessary to clean the remainder of the register
in case ->len is NOT a multiple of the register size, so make it
conditional just like nft_payload.c does.

The bug was added in 4.1 cycle and then copied/inherited when
tcp/sctp and ip option support was added.

Bug reported by Zero Day Initiative project (ZDI-CAN-21950,
ZDI-CAN-21951, ZDI-CAN-21961).

## References
- https://git.kernel.org/stable/c/1ad7b189cc1411048434e8595ffcbe7873b71082
- https://git.kernel.org/stable/c/28a97c43c9e32f437ebb8d6126f9bb7f3ca9521a
- https://git.kernel.org/stable/c/a7d86a77c33ba1c357a7504341172cc1507f0698
- https://git.kernel.org/stable/c/c8f292322ff16b9a2272a67de396c09a50e09dce
- https://git.kernel.org/stable/c/cf39c4f77a773a547ac2bcf30ecdd303bb0c80cb
- https://git.kernel.org/stable/c/d9ebfc0f21377690837ebbd119e679243e0099cc
- https://git.kernel.org/stable/c/fd94d9dadee58e09b49075240fe83423eb1dcd36
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52628.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52628
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
