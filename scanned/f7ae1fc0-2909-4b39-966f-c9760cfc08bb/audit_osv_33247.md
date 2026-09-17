# [C] tls: make sure to abort the stream if headers are bogus

## Summary
Severity: Critical
Advisory: CVE-2025-39946
Aliases: A-432728472, A-446648770, ASB-A-432728472, ASB-A-446648770
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2025-39946
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.154, >=6.2.0 <6.6.108, >=6.7.0 <6.12.49, >=6.13.0 <6.16.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

tls: make sure to abort the stream if headers are bogus

Normally we wait for the socket to buffer up the whole record
before we service it. If the socket has a tiny buffer, however,
we read out the data sooner, to prevent connection stalls.
Make sure that we abort the connection when we find out late
that the record is actually invalid. Retrying the parsing is
fine in itself but since we copy some more data each time
before we parse we can overflow the allocated skb space.

Constructing a scenario in which we're under pressure without
enough data in the socket to parse the length upfront is quite
hard. syzbot figured out a way to do this by serving us the header
in small OOB sends, and then filling in the recvbuf with a large
normal send.

Make sure that tls_rx_msg_size() aborts strp, if we reach
an invalid record there's really no way to recover.

## References
- https://git.kernel.org/stable/c/0aeb54ac4cd5cf8f60131b4d9ec0b6dc9c27b20d
- https://git.kernel.org/stable/c/208640e6225cc929a05adbf79d1df558add3e231
- https://git.kernel.org/stable/c/4cefe5be73886f383639fe0850bb72d5b568a7b9
- https://git.kernel.org/stable/c/61ca2da5fb8f433ce8bbd1657c84a86272133e6b
- https://git.kernel.org/stable/c/b36462146d86b1f22e594fe4dae611dffacfb203
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39946.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39946
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
