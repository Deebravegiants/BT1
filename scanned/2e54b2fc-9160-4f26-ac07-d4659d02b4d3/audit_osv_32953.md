# [H] virtio-net: xsk: rx: fix the frame's length check

## Summary
Severity: High
Advisory: CVE-2025-38413
Ecosystem: Linux
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38413
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.37, >=6.13.0 <6.15.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

virtio-net: xsk: rx: fix the frame's length check

When calling buf_to_xdp, the len argument is the frame data's length
without virtio header's length (vi->hdr_len). We check that len with

	xsk_pool_get_rx_frame_size() + vi->hdr_len

to ensure the provided len does not larger than the allocated chunk
size. The additional vi->hdr_len is because in virtnet_add_recvbuf_xsk,
we use part of XDP_PACKET_HEADROOM for virtio header and ask the vhost
to start placing data from

	hard_start + XDP_PACKET_HEADROOM - vi->hdr_len
not
	hard_start + XDP_PACKET_HEADROOM

But the first buffer has virtio_header, so the maximum frame's length in
the first buffer can only be

	xsk_pool_get_rx_frame_size()
not
	xsk_pool_get_rx_frame_size() + vi->hdr_len

like in the current check.

This commit adds an additional argument to buf_to_xdp differentiate
between the first buffer and other ones to correctly calculate the maximum
frame's length.

## References
- https://git.kernel.org/stable/c/5177373c31318c3c6a190383bfd232e6cf565c36
- https://git.kernel.org/stable/c/6013bb6bc24c2cac3f45b37a15b71b232a5b00ff
- https://git.kernel.org/stable/c/892f6ed9a4a38bb3360fdff091b9241cfa105b61
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38413.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38413
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
