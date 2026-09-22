# [H] accel/qaic: tighten bounds checking in decode_message()

## Summary
Severity: High
Advisory: CVE-2023-53493
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2023-53493
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.4.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/qaic: tighten bounds checking in decode_message()

Copy the bounds checking from encode_message() to decode_message().

This patch addresses the following concerns.  Ensure that there is
enough space for at least one header so that we don't have a negative
size later.

	if (msg_hdr_len < sizeof(*trans_hdr))

Ensure that we have enough space to read the next header from the
msg->data.

	if (msg_len > msg_hdr_len - sizeof(*trans_hdr))
		return -EINVAL;

Check that the trans_hdr->len is not below the minimum size:

	if (hdr_len < sizeof(*trans_hdr))

This minimum check ensures that we don't corrupt memory in
decode_passthrough() when we do.

	memcpy(out_trans->data, in_trans->data, len - sizeof(in_trans->hdr));

And finally, use size_add() to prevent an integer overflow:

	if (size_add(msg_len, hdr_len) > msg_hdr_len)

## References
- https://git.kernel.org/stable/c/51b56382ed2a2b03347372272362b3baa623ed1e
- https://git.kernel.org/stable/c/57d14cb3bae4619ce2fb5235cb318c3d5d8f53fd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53493.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53493
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
