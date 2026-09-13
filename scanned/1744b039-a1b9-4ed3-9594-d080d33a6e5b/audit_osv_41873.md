# [H] rxrpc: Fix DATA decrypt vs splice() by copying data to buffer in recvmsg

## Summary
Severity: High
Advisory: CVE-2026-64026
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64026
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix DATA decrypt vs splice() by copying data to buffer in recvmsg

This improves the fix for CVE-2026-43500.

Fix the pagecache corruption from in-place decryption of a DATA packet
transmitted locally by splice() by getting rid of the packet sharing in the
I/O thread and unconditionally extracting the packet content into a bounce
buffer in which the buffer is decrypted.  recvmsg() (or the kernel
equivalent) then copies the data from the bounce buffer to the destination
buffer.  The sk_buff then remains unmodified.

This has an additional advantage in that the packet is then arranged in the
buffer with the correct alignment required for the crypto algorithms to
process directly.  The performance of the crypto does seem to be a little
faster and, surprisingly, the unencrypted performance doesn't seem to
change much - possibly due to removing complexity from the I/O thread.

Yet another advantage is that the I/O thread doesn't have to copy packets
which would slow down packet distribution, ACK generation, etc..

The buffer belongs to the call and is allocated initially at 2K,
sufficiently large to hold a whole jumbo subpacket, but the buffer will be
increased in size if needed.  However, to take this work, MSG_PEEK may
cause a later packet to be decrypted into the buffer, in which case the
earlier one will need re-decrypting for a subsequent recvmsg().

Note that rx_pkt_offset may legitimately see 0 as a valid offset now, so
switch to using USHRT_MAX to indicate an invalid offset.

Note also that I would generally prefer to replace the buffers of the
current sk_buff with a new kmalloc'd buffer of the right size, ditching the
old data and frags as this makes the handling of MSG_PEEK easier and
removes the re-decryption issue, but this looks like quite a complicated
thing to achieve.  skb_morph() looks half way to what I want, but I don't
want to have to allocate a new sk_buff.

## References
- https://git.kernel.org/stable/c/46cb765e2e5ad52303ea157e10d370bb6b7acbbf
- https://git.kernel.org/stable/c/a05bf6d9e621fa71e89ccebe3047ba45218d7b38
- https://git.kernel.org/stable/c/b94a6ccbaf1104dd980150a65fdeb2f69d17d2f5
- https://git.kernel.org/stable/c/c580087743712112778a06d65a4074053072d7bf
- https://git.kernel.org/stable/c/d2bc90cf6c75cb96d2ce549be6c35efa3099d25b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64026.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64026
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
