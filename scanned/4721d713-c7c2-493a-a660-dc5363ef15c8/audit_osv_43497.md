# [C] bnxt: fix head underflow on XDP head-grow

## Summary
Severity: Critical
Advisory: CVE-2026-74269
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74269
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bnxt: fix head underflow on XDP head-grow

The xdp.py test test_xdp_native_adjst_head_grow_data crashes when run on
a bnxt machine (and also crashes in NIPA).

It seems that the bug is an underflow in bnxt_rx_multi_page_skb, which
builds the skb head:

  napi_build_skb(data_ptr - bp->rx_offset, rxr->rx_page_size);

The problem with this expression is that in page mode, rx_offset is:

  bp->rx_offset = NET_IP_ALIGN + XDP_PACKET_HEADROOM;

Which evaluates (at least on x86_64) to 258.

The test test_xdp_native_adjst_head_grow_data tests a case where the
head is adjusted by -256.

When this test runs, data_ptr is shifted to frag_start + 2 (where
frag_start = page_address(page) + offset).

Then, bnxt_rx_multi_page_skb is invoked and the napi_build_skb
expression subtracts 258, landing at an address before frag_start. This
could be either the previous fragment or the previous physical page when
the offset is < 256 (e.g. if the fragment started at offset 0).

When the skb is freed, the page pool fragment reference is dropped on
either the wrong page or the wrong frag of the right page. In either
case, the corrupted reference count can lead to the page being
prematurely recycled while still in use. Once (incorrectly) recycled, it
can be handed out again and on driver teardown this would result in a
double free.

The commit under fixes updated this code to handle the case where the
native page size is >= 64k, but it unintentionally broke the head grow
case.

To fix this, add an offset field to struct bnxt_sw_rx_bd, mirroring the
existing offset field in struct bnxt_sw_rx_agg_bd. Populate it on
allocation and preserve it on reuse.

In bnxt_rx_multi_page_skb, use the newly added offset field to compute
the fragment start and pass that to napi_build_skb. Adjust the layout
with skb_reserve.

There are two cases, the non-adjustment case and the adjustment case.

In both cases, the skb is built at page_address(page) + offset to
account for the case where the native page size >= 64K and skb_reserve
is called with data_ptr - (page_address(page) + offset). That
difference equals bp->rx_offset when data_ptr was not moved, or
bp->rx_offset + xdp_adjust when XDP adjusted the head.

Re-running the failing test with this commit applied causes the test to
run successfully to completion.

The other rx_skb_func implementations don't have this issue.

## References
- https://git.kernel.org/stable/c/bb72b1c6755631c74b7e0878ee55bb81c06776c0
- https://git.kernel.org/stable/c/e26657fe3b85c068b01f42bb0c602f242d643ba9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74269.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74269
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
