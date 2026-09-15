# [H] libceph: just wait for more data to be available on the socket

## Summary
Severity: High
Advisory: CVE-2023-52636
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2024-04-02
Source: https://osv.dev/vulnerability/CVE-2023-52636
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.17, >=6.7.0 <6.7.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: just wait for more data to be available on the socket

A short read may occur while reading the message footer from the
socket.  Later, when the socket is ready for another read, the
messenger invokes all read_partial_*() handlers, including
read_partial_sparse_msg_data().  The expectation is that
read_partial_sparse_msg_data() would bail, allowing the messenger to
invoke read_partial() for the footer and pick up where it left off.

However read_partial_sparse_msg_data() violates that and ends up
calling into the state machine in the OSD client.  The sparse-read
state machine assumes that it's a new op and interprets some piece of
the footer as the sparse-read header and returns bogus extents/data
length, etc.

To determine whether read_partial_sparse_msg_data() should bail, let's
reuse cursor->total_resid.  Because once it reaches to zero that means
all the extents and data have been successfully received in last read,
else it could break out when partially reading any of the extents and
data.  And then osd_sparse_read() could continue where it left off.

[ idryomov: changelog ]

## References
- https://git.kernel.org/stable/c/8e46a2d068c92a905d01cbb018b00d66991585ab
- https://git.kernel.org/stable/c/bd9442e553ab8bf74b8be3b3c0a43bf4af4dc9b8
- https://git.kernel.org/stable/c/da9c33a70f095d5d55c36d0bfeba969e31de08ae
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52636.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52636
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
