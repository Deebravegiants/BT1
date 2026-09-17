# [M] CVE-2021-47587

## Summary
Severity: Medium
Advisory: CVE-2021-47587
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2021-47587
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: systemport: Add global locking for descriptor lifecycle

The descriptor list is a shared resource across all of the transmit queues, and
the locking mechanism used today only protects concurrency across a given
transmit queue between the transmit and reclaiming. This creates an opportunity
for the SYSTEMPORT hardware to work on corrupted descriptors if we have
multiple producers at once which is the case when using multiple transmit
queues.

This was particularly noticeable when using multiple flows/transmit queues and
it showed up in interesting ways in that UDP packets would get a correct UDP
header checksum being calculated over an incorrect packet length. Similarly TCP
packets would get an equally correct checksum computed by the hardware over an
incorrect packet length.

The SYSTEMPORT hardware maintains an internal descriptor list that it re-arranges
when the driver produces a new descriptor anytime it writes to the
WRITE_PORT_{HI,LO} registers, there is however some delay in the hardware to
re-organize its descriptors and it is possible that concurrent TX queues
eventually break this internal allocation scheme to the point where the
length/status part of the descriptor gets used for an incorrect data buffer.

The fix is to impose a global serialization for all TX queues in the short
section where we are writing to the WRITE_PORT_{HI,LO} registers which solves
the corruption even with multiple concurrent TX queues being used.

## References
- https://git.kernel.org/stable/c/f3fde37d3f0d429f0fcce214cb52588a9e21260e
- https://git.kernel.org/stable/c/595a684fa6f23b21958379a18cfa83862c73c2e1
- https://git.kernel.org/stable/c/6e1011cd183faae8daff275c72444edcdfe0d473
- https://git.kernel.org/stable/c/8b8e6e782456f1ce02a7ae914bbd5b1053f0b034
- https://git.kernel.org/stable/c/8ed2f5d08d6e59f8c78b2869bfb95d0be32c094c
- https://git.kernel.org/stable/c/c675256a7f131f5ba3f331efb715e8f31ea0e392
- https://git.kernel.org/stable/c/de57f62f76450b934de8203711bdc4f7953c3421
- https://git.kernel.org/stable/c/eb4687c7442942e115420a30185f8d83faf37696
