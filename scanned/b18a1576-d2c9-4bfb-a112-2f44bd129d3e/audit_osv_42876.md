# [C] scsi: target: Bound PR-OUT TransportID parsing to the received buffer

## Summary
Severity: Critical
Advisory: CVE-2026-72084
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72084
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.38 <5.10.266, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: target: Bound PR-OUT TransportID parsing to the received buffer

core_scsi3_decode_spec_i_port() and core_scsi3_emulate_register_and_move()
hand the raw PERSISTENT RESERVE OUT parameter buffer to
target_parse_pr_out_transport_id() without telling it how many bytes are
valid.  For an iSCSI TransportID (FORMAT CODE 01b),
iscsi_parse_pr_out_transport_id() locates the ",i,0x" ISID separator with
an unbounded strstr() (and on the error path prints the name with a further
unbounded "%s").  An initiator can submit a TransportID whose iSCSI name
contains neither a ",i,0x" substring nor a NUL terminator, filling the
parameter list to its end, so the scan runs off the end of the buffer.

When the parameter list spans more than one page the buffer is a multi-page
vmap (transport_kmap_data_sg()), so the over-read walks into the trailing
vmalloc guard page and oopses (KASAN: vmalloc-out-of-bounds in strstr).  It
is reachable by any fabric that delivers a PR OUT to a device exported
through an iSCSI TPG, including a guest via vhost-scsi.

Pass the number of received bytes down to the parser and validate the iSCSI
TransportID's own self-described length (ADDITIONAL LENGTH + 4) once, up
front: reject it if it is below the spc4r17 minimum or larger than the
received buffer, then bound the separator search, the ISID walk and the
name copy by that length.  This is the length check the callers already
perform after the parse (core_scsi3_decode_spec_i_port() compares tid_len
against tpdl, core_scsi3_emulate_register_and_move() validates it against
data_length), moved ahead of the scan.  Also drop the unbounded "%s" of the
unterminated name.

Add per-format explicit name-length checks before copying into i_str,
rather than silently truncating with min_t: for FORMAT CODE 00b reject if
the descriptor body (tid_len - 4 bytes) cannot fit in
i_str[TRANSPORT_IQN_LEN]; for FORMAT CODE 01b reject if the name portion
(from &buf[4] up to the separator) cannot fit.  Both checks make the bounds
intent explicit at each format branch.

While here, also reject a FORMAT CODE 01b TransportID whose ",i,0x"
separator sits at the very end of the descriptor: that leaves an empty ISID
and points the returned port nexus pointer at buf + tid_len, one past the
descriptor, which the registration code (__core_scsi3_locate_pr_reg(),
__core_scsi3_alloc_registration()) then dereferences as the ISID string --
the same over-read of the parameter buffer for a malformed descriptor.

## References
- https://git.kernel.org/stable/c/004ccd2d3b4ac36a300e05e01df152e5c02a5a82
- https://git.kernel.org/stable/c/03fbc7de8d5e85fc8420e57e8304c855efd453ab
- https://git.kernel.org/stable/c/555a89846ed888d7401b3f7200934c0fbedcbb46
- https://git.kernel.org/stable/c/6ca5de8782e67573a61a6736b6dc0ffe58dcdf59
- https://git.kernel.org/stable/c/842248047ef28dbf3b3f7f49a0ec315054d4dab8
- https://git.kernel.org/stable/c/88c67c3de914e19172e1d878a7625c5b06c20ec5
- https://git.kernel.org/stable/c/9298078a8f7d8181a04614a34ab655ccdf038204
- https://git.kernel.org/stable/c/d04a179085c262c9ed577d0a4cbc6482ff1fd9a3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72084.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72084
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
