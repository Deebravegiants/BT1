# [H] tpm: Make the TPM character devices non-seekable

## Summary
Severity: High
Advisory: CVE-2026-72135
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72135
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

tpm: Make the TPM character devices non-seekable

The TPM character devices expose a sequential command/response
interface, but their open handlers leave FMODE_PREAD and FMODE_PWRITE
enabled.

After a command leaves a response pending, pread(fd, buf, 16, 0x1400)
passes 0x1400 as *off to tpm_common_read(). The transfer length is
bounded by response_length, but the offset is used unchecked when
forming data_buffer + *off. A sufficiently large offset therefore causes
an out-of-bounds heap read through copy_to_user() and, if the copy
succeeds, an out-of-bounds zero-write through the following memset().

Positional I/O does not provide coherent semantics for this interface.
An arbitrary pread offset cannot represent how much of a response has
been consumed sequentially. The write callback always stores a command
at the start of data_buffer, while pwrite() does not update file->f_pos
and can leave the sequential read cursor stale.

Call nonseekable_open() from both open handlers. This removes
FMODE_PREAD and FMODE_PWRITE, causing positional reads and writes to
fail with -ESPIPE before reaching the TPM callbacks, and explicitly
marks the files non-seekable. Normal read() and write() continue to use
the existing sequential f_pos cursor, leaving the response state machine
unchanged.

Tested on Linux 6.12 with KASAN and a swtpm TPM2 device:

 - sequential partial reads returned the complete response
 - pread() and preadv() with offset 0x1400 returned -ESPIPE
 - pwrite() and pwritev() with offset zero returned -ESPIPE
 - the pending response remained intact after the rejected operations
 - a subsequent normal command/response cycle completed normally
 - no KASAN report was produced.

## References
- https://git.kernel.org/stable/c/21a13f932972bc9836f58c44fcd47c62abdecd95
- https://git.kernel.org/stable/c/232dcf908eb7eb9d8046a9597975caf44270966e
- https://git.kernel.org/stable/c/947b773caaa548672184df025271b29bdc80b0f1
- https://git.kernel.org/stable/c/9c513dabd4540f811585a2087f23069767a284da
- https://git.kernel.org/stable/c/ada4b9a5087ea7f30dd8e4c6411a4fb6547eb1ed
- https://git.kernel.org/stable/c/dda695fab5e21f923d29e8cb01df256468ddfbd1
- https://git.kernel.org/stable/c/ed0ffc2c016629e40ba041ed0424a772d8b02e2c
- https://git.kernel.org/stable/c/f20d61c22bcaf172d6790b6500e3838e532e71c8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72135.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72135
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
