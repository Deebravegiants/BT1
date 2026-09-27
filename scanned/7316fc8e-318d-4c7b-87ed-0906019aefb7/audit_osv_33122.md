# [H] netfs: Fix unbuffered write error handling

## Summary
Severity: High
Advisory: CVE-2025-39723
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-39723
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.44, >=6.13.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfs: Fix unbuffered write error handling

If all the subrequests in an unbuffered write stream fail, the subrequest
collector doesn't update the stream->transferred value and it retains its
initial LONG_MAX value.  Unfortunately, if all active streams fail, then we
take the smallest value of { LONG_MAX, LONG_MAX, ... } as the value to set
in wreq->transferred - which is then returned from ->write_iter().

LONG_MAX was chosen as the initial value so that all the streams can be
quickly assessed by taking the smallest value of all stream->transferred -
but this only works if we've set any of them.

Fix this by adding a flag to indicate whether the value in
stream->transferred is valid and checking that when we integrate the
values.  stream->transferred can then be initialised to zero.

This was found by running the generic/750 xfstest against cifs with
cache=none.  It splices data to the target file.  Once (if) it has used up
all the available scratch space, the writes start failing with ENOSPC.
This causes ->write_iter() to fail.  However, it was returning
wreq->transferred, i.e. LONG_MAX, rather than an error (because it thought
the amount transferred was non-zero) and iter_file_splice_write() would
then try to clean up that amount of pipe bufferage - leading to an oops
when it overran.  The kernel log showed:

    CIFS: VFS: Send error in write = -28

followed by:

    BUG: kernel NULL pointer dereference, address: 0000000000000008

with:

    RIP: 0010:iter_file_splice_write+0x3a4/0x520
    do_splice+0x197/0x4e0

or:

    RIP: 0010:pipe_buf_release (include/linux/pipe_fs_i.h:282)
    iter_file_splice_write (fs/splice.c:755)

Also put a warning check into splice to announce if ->write_iter() returned
that it had written more than it was asked to.

## References
- https://git.kernel.org/stable/c/387164a2b97e1f5404c6d0049a7409bac7d2bc5b
- https://git.kernel.org/stable/c/a3de58b12ce074ec05b8741fa28d62ccb1070468
- https://git.kernel.org/stable/c/f08c80af3c9a9849cd178b4843b7c01d103506a1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39723.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39723
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
