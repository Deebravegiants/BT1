# [H] mptcp: fix data re-injection from stale subflow

## Summary
Severity: High
Advisory: CVE-2024-26826
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26826
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.149, >=5.16.0 <6.1.79, >=6.2.0 <6.6.18, >=6.7.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: fix data re-injection from stale subflow

When the MPTCP PM detects that a subflow is stale, all the packet
scheduler must re-inject all the mptcp-level unacked data. To avoid
acquiring unneeded locks, it first try to check if any unacked data
is present at all in the RTX queue, but such check is currently
broken, as it uses TCP-specific helper on an MPTCP socket.

Funnily enough fuzzers and static checkers are happy, as the accessed
memory still belongs to the mptcp_sock struct, and even from a
functional perspective the recovery completed successfully, as
the short-cut test always failed.

A recent unrelated TCP change - commit d5fed5addb2b ("tcp: reorganize
tcp_sock fast path variables") - exposed the issue, as the tcp field
reorganization makes the mptcp code always skip the re-inection.

Fix the issue dropping the bogus call: we are on a slow path, the early
optimization proved once again to be evil.

## References
- https://git.kernel.org/stable/c/624902eab7abcb8731b333ec73f206d38d839cd8
- https://git.kernel.org/stable/c/6673d9f1c2cd984390550dbdf7d5ae07b20abbf8
- https://git.kernel.org/stable/c/6f95120f898b40d13fd441225ef511307853c9c2
- https://git.kernel.org/stable/c/b609c783c535493aa3fca22c7e40a120370b1ca5
- https://git.kernel.org/stable/c/b6c620dc43ccb4e802894e54b651cf81495e9598
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26826.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26826
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
