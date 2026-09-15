# [M] CVE-2019-3837

## Summary
Severity: Medium
Advisory: CVE-2019-3837
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2019-04-11
Source: https://osv.dev/vulnerability/CVE-2019-3837
Type: osv

## Details
It was found that the net_dma code in tcp_recvmsg() in the 2.6.32 kernel as shipped in RHEL6 is thread-unsafe. So an unprivileged multi-threaded userspace application calling recvmsg() for the same network socket in parallel executed on ioatdma-enabled hardware with net_dma enabled can leak the memory, crash the host leading to a denial-of-service or cause a random memory corruption.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3837
