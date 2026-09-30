# [C] RDMA/rxe: Validate pad and ICRC before payload_size() in rxe_rcv

## Summary
Severity: Critical
Advisory: CVE-2026-46043
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46043
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.86, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/rxe: Validate pad and ICRC before payload_size() in rxe_rcv

rxe_rcv() currently checks only that the incoming packet is at least
header_size(pkt) bytes long before payload_size() is used.

However, payload_size() subtracts both the attacker-controlled BTH pad
field and RXE_ICRC_SIZE from pkt->paylen:

  payload_size = pkt->paylen - offset[RXE_PAYLOAD] - bth_pad(pkt)
                 - RXE_ICRC_SIZE

This means a short packet can still make payload_size() underflow even
if it includes enough bytes for the fixed headers. Simply requiring
header_size(pkt) + RXE_ICRC_SIZE is not sufficient either, because a
packet with a forged non-zero BTH pad can still leave payload_size()
negative and pass an underflowed value to later receive-path users.

Fix this by validating pkt->paylen against the full minimum length
required by payload_size(): header_size(pkt) + bth_pad(pkt) +
RXE_ICRC_SIZE.

## References
- https://git.kernel.org/stable/c/2c0d71ef12f46c57d37bc571f3f2797db7eb50cc
- https://git.kernel.org/stable/c/2fd4f8b749309a61c3f3f88ee8891d94f79e1240
- https://git.kernel.org/stable/c/5fedefec757192dcaad29a664ac332c7601be144
- https://git.kernel.org/stable/c/7244491dab347f648e661da96dc0febadd9daec3
- https://git.kernel.org/stable/c/9b924f3a26b21330a837cfe72e819b6393bbeeaa
- https://git.kernel.org/stable/c/c4376c672c3648d5bdc31dfffc329d07164f93c4
- https://git.kernel.org/stable/c/e8ee0e792d475b1067c199ef0af1b6221fa6f43d
- https://git.kernel.org/stable/c/f83519a4c122c9c7a850a2197648a9ff4c67c520
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46043.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46043
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
