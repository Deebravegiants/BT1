# [C] ice: fix Rx page leak on multi-buffer frames

## Summary
Severity: Critical
Advisory: CVE-2025-39948
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2025-39948
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.49, >=6.13.0 <6.16.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ice: fix Rx page leak on multi-buffer frames

The ice_put_rx_mbuf() function handles calling ice_put_rx_buf() for each
buffer in the current frame. This function was introduced as part of
handling multi-buffer XDP support in the ice driver.

It works by iterating over the buffers from first_desc up to 1 plus the
total number of fragments in the frame, cached from before the XDP program
was executed.

If the hardware posts a descriptor with a size of 0, the logic used in
ice_put_rx_mbuf() breaks. Such descriptors get skipped and don't get added
as fragments in ice_add_xdp_frag. Since the buffer isn't counted as a
fragment, we do not iterate over it in ice_put_rx_mbuf(), and thus we don't
call ice_put_rx_buf().

Because we don't call ice_put_rx_buf(), we don't attempt to re-use the
page or free it. This leaves a stale page in the ring, as we don't
increment next_to_alloc.

The ice_reuse_rx_page() assumes that the next_to_alloc has been incremented
properly, and that it always points to a buffer with a NULL page. Since
this function doesn't check, it will happily recycle a page over the top
of the next_to_alloc buffer, losing track of the old page.

Note that this leak only occurs for multi-buffer frames. The
ice_put_rx_mbuf() function always handles at least one buffer, so a
single-buffer frame will always get handled correctly. It is not clear
precisely why the hardware hands us descriptors with a size of 0 sometimes,
but it happens somewhat regularly with "jumbo frames" used by 9K MTU.

To fix ice_put_rx_mbuf(), we need to make sure to call ice_put_rx_buf() on
all buffers between first_desc and next_to_clean. Borrow the logic of a
similar function in i40e used for this same purpose. Use the same logic
also in ice_get_pgcnts().

Instead of iterating over just the number of fragments, use a loop which
iterates until the current index reaches to the next_to_clean element just
past the current frame. Unlike i40e, the ice_put_rx_mbuf() function does
call ice_put_rx_buf() on the last buffer of the frame indicating the end of
packet.

For non-linear (multi-buffer) frames, we need to take care when adjusting
the pagecnt_bias. An XDP program might release fragments from the tail of
the frame, in which case that fragment page is already released. Only
update the pagecnt_bias for the first descriptor and fragments still
remaining post-XDP program. Take care to only access the shared info for
fragmented buffers, as this avoids a significant cache miss.

The xdp_xmit value only needs to be updated if an XDP program is run, and
only once per packet. Drop the xdp_xmit pointer argument from
ice_put_rx_mbuf(). Instead, set xdp_xmit in the ice_clean_rx_irq() function
directly. This avoids needing to pass the argument and avoids an extra
bit-wise OR for each buffer in the frame.

Move the increment of the ntc local variable to ensure its updated *before*
all calls to ice_get_pgcnts() or ice_put_rx_mbuf(), as the loop logic
requires the index of the element just after the current frame.

Now that we use an index pointer in the ring to identify the packet, we no
longer need to track or cache the number of fragments in the rx_ring.

## References
- https://git.kernel.org/stable/c/80555adb5c892f0e21d243ae96ed997ee520aea9
- https://git.kernel.org/stable/c/84bf1ac85af84d354c7a2fdbdc0d4efc8aaec34b
- https://git.kernel.org/stable/c/fcb5718ebfe7fd64144e3399280440cce361a3ae
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39948.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39948
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
