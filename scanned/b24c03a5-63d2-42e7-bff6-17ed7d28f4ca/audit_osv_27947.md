# [H] netfilter: nf_conntrack_h323: Add protection for bmp length out of range

## Summary
Severity: High
Advisory: CVE-2024-26851
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26851
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.17 <4.19.310, >=4.20.0 <5.4.272, >=5.5.0 <5.10.213, >=5.11.0 <5.15.152, >=5.16.0 <6.1.82, >=6.2.0 <6.6.22, >=6.7.0 <6.7.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_conntrack_h323: Add protection for bmp length out of range

UBSAN load reports an exception of BRK#5515 SHIFT_ISSUE:Bitwise shifts
that are out of bounds for their data type.

vmlinux   get_bitmap(b=75) + 712
<net/netfilter/nf_conntrack_h323_asn1.c:0>
vmlinux   decode_seq(bs=0xFFFFFFD008037000, f=0xFFFFFFD008037018, level=134443100) + 1956
<net/netfilter/nf_conntrack_h323_asn1.c:592>
vmlinux   decode_choice(base=0xFFFFFFD0080370F0, level=23843636) + 1216
<net/netfilter/nf_conntrack_h323_asn1.c:814>
vmlinux   decode_seq(f=0xFFFFFFD0080371A8, level=134443500) + 812
<net/netfilter/nf_conntrack_h323_asn1.c:576>
vmlinux   decode_choice(base=0xFFFFFFD008037280, level=0) + 1216
<net/netfilter/nf_conntrack_h323_asn1.c:814>
vmlinux   DecodeRasMessage() + 304
<net/netfilter/nf_conntrack_h323_asn1.c:833>
vmlinux   ras_help() + 684
<net/netfilter/nf_conntrack_h323_main.c:1728>
vmlinux   nf_confirm() + 188
<net/netfilter/nf_conntrack_proto.c:137>

Due to abnormal data in skb->data, the extension bitmap length
exceeds 32 when decoding ras message then uses the length to make
a shift operation. It will change into negative after several loop.
UBSAN load could detect a negative shift as an undefined behaviour
and reports exception.
So we add the protection to avoid the length exceeding 32. Or else
it will return out of range error and stop decoding.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/014a807f1cc9c9d5173c1cd935835553b00d211c
- https://git.kernel.org/stable/c/39001e3c42000e7c2038717af0d33c32319ad591
- https://git.kernel.org/stable/c/4bafcc43baf7bcf93566394dbd15726b5b456b7a
- https://git.kernel.org/stable/c/767146637efc528b5e3d31297df115e85a2fd362
- https://git.kernel.org/stable/c/80ee5054435a11c87c9a4f30f1ff750080c96416
- https://git.kernel.org/stable/c/98db42191329c679f4ca52bec0b319689e1ad8cb
- https://git.kernel.org/stable/c/b3c0f553820516ad4b62a9390ecd28d6f73a7b13
- https://git.kernel.org/stable/c/ccd1108b16ab572d9bf635586b0925635dbd6bbc
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26851.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26851
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
