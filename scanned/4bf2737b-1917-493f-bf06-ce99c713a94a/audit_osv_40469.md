# [H] netfilter: nft_ct: bail out on template ct in get eval

## Summary
Severity: High
Advisory: CVE-2026-53267
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53267
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nft_ct: bail out on template ct in get eval

I noticed this issue while looking at a historic syzbot report [1].

A rule like the one below is enough to trigger the bug:

    table ip t {
        chain pre {
            type filter hook prerouting priority raw;
            ct zone set 1
            ct original saddr 1.2.3.4 accept
        }
    }

The first expression attaches a per-cpu template ct via
nft_ct_set_zone_eval() (nf_ct_tmpl_alloc -> kzalloc, tuple is all
zero, nf_ct_l3num(ct) == 0). The next expression then calls
nft_ct_get_eval() on the same skb, treats the template as a real ct
and hits the 16-byte memcpy path. With dreg at NFT_REG32_15 this
overflows past struct nft_regs on the kernel stack; with smaller
dreg values it silently clobbers adjacent registers.

Reject template ct at the eval entry and in nft_ct_get_fast_eval(),
mirroring the check nft_ct_set_eval() already has. Additionally,
bound the address copy in NFT_CT_SRC / NFT_CT_DST by priv->len
instead of by nf_ct_l3num(ct): nf_ct_get_tuple() zeroes the tuple
before pkt_to_tuple() fills in only the protocol-relevant leading
bytes, so the trailing bytes of tuple->{src,dst}.u3.all are
well-defined zero. priv->len is validated at rule load, so the
copy size is now bounded by the destination register rather than
by an untrusted field on the conntrack.

[1]: https://syzkaller.appspot.com/bug?id=389cf09cb72926114fce90dc85a2c3231dcb647c

## References
- https://git.kernel.org/stable/c/2e154b5f53f1b0b490c7b8b02499f90feb86b1d5
- https://git.kernel.org/stable/c/3027ecbdb5fdf9200251c21d4818e4c447ef78e1
- https://git.kernel.org/stable/c/8470f676eadeab99132708acb1a85915664d6115
- https://git.kernel.org/stable/c/af80f78ce984649e1698b841cd33f4fa505ad828
- https://git.kernel.org/stable/c/f071b0bf078146368d18e4eec386bf2ddc0ab7e0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53267.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53267
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
