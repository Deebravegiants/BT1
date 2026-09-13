# [M] TFTP small blocksize heap buffer overflow

## Summary
Severity: Medium
Advisory: CURL-CVE-2019-5482
Aliases: CVE-2019-5482
Published: 2019-09-11
Source: https://osv.dev/vulnerability/CURL-CVE-2019-5482
Type: osv

## Details
libcurl contains a heap buffer overflow in the function
(`tftp_receive_packet()`) that receives data from a TFTP server. It can call
`recvfrom()` with the default size for the buffer rather than with the size
that was used to allocate it. Thus, the content that might overwrite the heap
memory is controlled by the server.

This flaw is only triggered if the TFTP server sends an `OACK` without the
`BLKSIZE` option, when a `BLKSIZE` smaller than 512 bytes was requested by the
TFTP client.  `OACK` is a TFTP extension and is not used by all TFTP servers.

Users choosing a smaller block size than default should be rare as the primary
use case for changing the size is to make it larger.

It is rare for users to use TFTP across the Internet. It is most commonly used
within local networks. TFTP as a protocol is always inherently insecure.

This issue was introduced by the add of the TFTP `BLKSIZE` option handling. It
was previously incompletely fixed by an almost identical issue called
CVE-2019-5436.
