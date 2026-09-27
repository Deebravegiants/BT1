# [C] tcp: do not accept ACK of bytes we never sent

## Summary
Severity: Critical
Advisory: CVE-2023-52881
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-29
Source: https://osv.dev/vulnerability/CVE-2023-52881
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <4.14.333, >=4.15.0 <4.19.302, >=4.20.0 <5.4.264, >=5.5.0 <5.10.204, >=5.11.0 <5.15.143, >=5.16.0 <6.1.68, >=6.2.0 <6.6.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: do not accept ACK of bytes we never sent

This patch is based on a detailed report and ideas from Yepeng Pan
and Christian Rossow.

ACK seq validation is currently following RFC 5961 5.2 guidelines:

   The ACK value is considered acceptable only if
   it is in the range of ((SND.UNA - MAX.SND.WND) <= SEG.ACK <=
   SND.NXT).  All incoming segments whose ACK value doesn't satisfy the
   above condition MUST be discarded and an ACK sent back.  It needs to
   be noted that RFC 793 on page 72 (fifth check) says: "If the ACK is a
   duplicate (SEG.ACK < SND.UNA), it can be ignored.  If the ACK
   acknowledges something not yet sent (SEG.ACK > SND.NXT) then send an
   ACK, drop the segment, and return".  The "ignored" above implies that
   the processing of the incoming data segment continues, which means
   the ACK value is treated as acceptable.  This mitigation makes the
   ACK check more stringent since any ACK < SND.UNA wouldn't be
   accepted, instead only ACKs that are in the range ((SND.UNA -
   MAX.SND.WND) <= SEG.ACK <= SND.NXT) get through.

This can be refined for new (and possibly spoofed) flows,
by not accepting ACK for bytes that were never sent.

This greatly improves TCP security at a little cost.

I added a Fixes: tag to make sure this patch will reach stable trees,
even if the 'blamed' patch was adhering to the RFC.

tp->bytes_acked was added in linux-4.2

Following packetdrill test (courtesy of Yepeng Pan) shows
the issue at hand:

0 socket(..., SOCK_STREAM, IPPROTO_TCP) = 3
+0 setsockopt(3, SOL_SOCKET, SO_REUSEADDR, [1], 4) = 0
+0 bind(3, ..., ...) = 0
+0 listen(3, 1024) = 0

// ---------------- Handshake ------------------- //

// when window scale is set to 14 the window size can be extended to
// 65535 * (2^14) = 1073725440. Linux would accept an ACK packet
// with ack number in (Server_ISN+1-1073725440. Server_ISN+1)
// ,though this ack number acknowledges some data never
// sent by the server.

+0 < S 0:0(0) win 65535 <mss 1400,nop,wscale 14>
+0 > S. 0:0(0) ack 1 <...>
+0 < . 1:1(0) ack 1 win 65535
+0 accept(3, ..., ...) = 4

// For the established connection, we send an ACK packet,
// the ack packet uses ack number 1 - 1073725300 + 2^32,
// where 2^32 is used to wrap around.
// Note: we used 1073725300 instead of 1073725440 to avoid possible
// edge cases.
// 1 - 1073725300 + 2^32 = 3221241997

// Oops, old kernels happily accept this packet.
+0 < . 1:1001(1000) ack 3221241997 win 65535

// After the kernel fix the following will be replaced by a challenge ACK,
// and prior malicious frame would be dropped.
+0 > . 1:1(0) ack 1001

## References
- https://git.kernel.org/stable/c/008b807fe487e0b15a3a6c39add4eb477f73e440
- https://git.kernel.org/stable/c/0d4e0afdd6658cd21dd5be61880411a2553fd1fc
- https://git.kernel.org/stable/c/2087d53a66e97a5eb5d1bf558d5bef9e5f891757
- https://git.kernel.org/stable/c/3d501dd326fb1c73f1b8206d4c6e1d7b15c07e27
- https://git.kernel.org/stable/c/458f07ffeccd17f99942311e09ef574ddf4a414a
- https://git.kernel.org/stable/c/69eae75ca5255e876628ac5cee9eaab31f644b57
- https://git.kernel.org/stable/c/7ffff0cc929fdfc62a74b384c4903d6496c910f0
- https://git.kernel.org/stable/c/b17a886ed29f3b70b78ccf632dad03e0c69e3c1a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52881.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52881
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
