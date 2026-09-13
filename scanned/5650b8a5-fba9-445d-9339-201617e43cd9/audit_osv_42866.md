# [C] gve: fix header buffer corruption with header-split and HW-GRO

## Summary
Severity: Critical
Advisory: CVE-2026-72046
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72046
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.101, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

gve: fix header buffer corruption with header-split and HW-GRO

The DQO RX datapath programs a per-buffer-queue-descriptor
header_buf_addr at post time and reads the split header back at
completion time. Both the post and the read currently index the
header buffer by queue position rather than by the buffer's identity:

  - post (gve_rx_post_buffers_dqo): header_buf_addr is computed from
    bufq->tail
  - read (gve_rx_dqo): the header is read from desc_idx (the completion
    queue head index)

This relies on the buffer-queue index and the completion-queue index
being equal for the start of every packet, i.e. on the device consuming
posted buffers and returning completions in the exact same order. That
assumption does not hold once HW-GRO is enabled with multiple
flows: coalesced segments are accepted and completed in an order that
may differ from the order buffers were posted, and segments from
different flows may interleave.

That results in two problems:

1. Wrong header slot on read. Because the read offset is derived from
   the completion index (desc_idx) while the device wrote the header to
   the address programmed for the buffer's buf_id, the driver can copy
   a header belonging to a different packet. This shows up as
   throughput drop (about 30% drop and large numbers of TCP
   retransmissions) with header-split and HW-GRO both enabled and many
   streams.

2. Header buffer reused while still owned by the device. The driver
   advances bufq->head by one per completion and re-posts buffers based
   on that. Arrival of N RX completions only guarantees that at least N
   RX buffer descriptors have been read by the device. It does not
   guarantee that the device has relinquished the ownership of all the
   buffers corresponding to those N descriptors. With out-of-order
   completions (e.g. the completion for a packet copied into buffer N
   arrives before the completion for a packet copied into buffer N-1),
   the driver can re-post and overwrite a header buffer that the device
   is still going to write into, corrupting the header of a packet
   whose completion has not yet been processed.

Fix both issues by indexing the header buffer by buf_id on both the post
and read paths. Reading from buf_id's slot is therefore always correct
regardless of completion ordering (fixes problem 1).

Indexing by buf_id also ties each header slot to the lifetime of its
buffer state. A buffer state is only returned to the free/recycle lists
when its own completion (buf_id) is processed, so its header slot can
only be re-posted after the device is done with it. This makes header
slot reuse safe under out-of-order completions (fixes problem 2).

Allocate (gve_rx_alloc_hdr_bufs) and free (gve_rx_free_hdr_bufs) the
header buffers based on num_buf_states to match the buf_id indexing.

## References
- https://git.kernel.org/stable/c/35267819b25074084130b6a7be18bbaf44d3ae74
- https://git.kernel.org/stable/c/84d3753d4bf284ef770ead6dee2270aaabb3ef41
- https://git.kernel.org/stable/c/9f8e7f59b0c2f466be74bd923726b0f5496c27ad
- https://git.kernel.org/stable/c/d676c9a73bdcd8237425dbb826f2bd1a25c36e40
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72046.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72046
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
