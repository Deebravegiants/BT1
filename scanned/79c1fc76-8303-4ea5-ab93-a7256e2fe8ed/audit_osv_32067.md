# [H] media: venus: hfi: add check to handle incorrect queue size

## Summary
Severity: High
Advisory: CVE-2025-23158
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2025-23158
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <5.4.293, >=5.5.0 <5.10.237, >=5.11.0 <5.15.181, >=5.16.0 <6.1.135, >=6.2.0 <6.6.88, >=6.7.0 <6.12.24, >=6.13.0 <6.13.12, >=6.14.0 <6.14.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: venus: hfi: add check to handle incorrect queue size

qsize represents size of shared queued between driver and video
firmware. Firmware can modify this value to an invalid large value. In
such situation, empty_space will be bigger than the space actually
available. Since new_wr_idx is not checked, so the following code will
result in an OOB write.
...
qsize = qhdr->q_size

if (wr_idx >= rd_idx)
 empty_space = qsize - (wr_idx - rd_idx)
....
if (new_wr_idx < qsize) {
 memcpy(wr_ptr, packet, dwords << 2) --> OOB write

Add check to ensure qsize is within the allocated size while
reading and writing packets into the queue.

## References
- https://git.kernel.org/stable/c/101a86619aab42bb61f2253bbf720121022eab86
- https://git.kernel.org/stable/c/1b86c1917e16bafbbb08ab90baaff533aa36c62d
- https://git.kernel.org/stable/c/32af5c1fdb9bc274f52ee0472d3b060b18e4aab4
- https://git.kernel.org/stable/c/40084302f639b3fe954398c5ba5ee556b7242b54
- https://git.kernel.org/stable/c/679424f8b31446f90080befd0300ea915485b096
- https://git.kernel.org/stable/c/69baf245b23e20efda0079238b27fc63ecf13de1
- https://git.kernel.org/stable/c/a45957bcde529169188929816775a575de77d84f
- https://git.kernel.org/stable/c/cf5f7bb4e0d786f4d9d50ae6b5963935eab71d75
- https://git.kernel.org/stable/c/edb89d69b1438681daaf5ca90aed3242df94cc96
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/23xxx/CVE-2025-23158.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-23158
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
