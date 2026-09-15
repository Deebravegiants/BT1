# [H] flow_dissector: do not dissect PPPoE PFC frames

## Summary
Severity: High
Advisory: CVE-2026-46306
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/CVE-2026-46306
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

flow_dissector: do not dissect PPPoE PFC frames

RFC 2516 Section 7 states that Protocol Field Compression (PFC) is NOT
RECOMMENDED for PPPoE. In practice, pppd does not support negotiating
PFC for PPPoE sessions, and the flow dissector driver has assumed an
uncompressed frame until the blamed commit.

During the review process of that commit [1], support for PFC is
suggested. However, having a compressed (1-byte) protocol field means
the subsequent PPP payload is shifted by one byte, causing 4-byte
misalignment for the network header and an unaligned access exception
on some architectures.

The exception can be reproduced by sending a PPPoE PFC frame to an
ethernet interface of a MIPS board, with RPS enabled, even if no PPPoE
session is active on that interface:

$ 0   : 00000000 80c40000 00000000 85144817
$ 4   : 00000008 00000100 80a75758 81dc9bb8
$ 8   : 00000010 8087ae2c 0000003d 00000000
$12   : 000000e0 00000039 00000000 00000000
$16   : 85043240 80a75758 81dc9bb8 00006488
$20   : 0000002f 00000007 85144810 80a70000
$24   : 81d1bda0 00000000
$28   : 81dc8000 81dc9aa8 00000000 805ead08
Hi    : 00009d51
Lo    : 2163358a
epc   : 805e91f0 __skb_flow_dissect+0x1b0/0x1b50
ra    : 805ead08 __skb_get_hash_net+0x74/0x12c
Status: 11000403        KERNEL EXL IE
Cause : 40800010 (ExcCode 04)
BadVA : 85144817
PrId  : 0001992f (MIPS 1004Kc)
Call Trace:
[<805e91f0>] __skb_flow_dissect+0x1b0/0x1b50
[<805ead08>] __skb_get_hash_net+0x74/0x12c
[<805ef330>] get_rps_cpu+0x1b8/0x3fc
[<805fca70>] netif_receive_skb_list_internal+0x324/0x364
[<805fd120>] napi_complete_done+0x68/0x2a4
[<8058de5c>] mtk_napi_rx+0x228/0xfec
[<805fd398>] __napi_poll+0x3c/0x1c4
[<805fd754>] napi_threaded_poll_loop+0x234/0x29c
[<805fd848>] napi_threaded_poll+0x8c/0xb0
[<80053544>] kthread+0x104/0x12c
[<80002bd8>] ret_from_kernel_thread+0x14/0x1c

Code: 02d51821  1060045b  00000000 <8c640000> 3084000f  2c820005  144001a2  00042080  8e220000

To reduce the attack surface and maintain performance, do not process
PPPoE PFC frames.

[1] https://lore.kernel.org/r/20220630231016.GA392@debian.home

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/0d00b9015069712944934bab09eaa6c542143049
- https://git.kernel.org/stable/c/18ae9eacfc95cc715c0606b2c86e8aa8a86cf3e3
- https://git.kernel.org/stable/c/6044392d9cace3a3672b02c8bc7d38b502e51734
- https://git.kernel.org/stable/c/7c93f353eab4ea911e394630f07d72e040a729d8
- https://git.kernel.org/stable/c/abc5bc84e0f2edc7ea2d437afa6ef3fe1fc43200
- https://git.kernel.org/stable/c/d6c19b31a3c1d519fabdcf0aa239e6b6109b9473
- https://git.kernel.org/stable/c/db104b0d8a7856397c0469d83a4289adf7c54863
- https://git.kernel.org/stable/c/e7c811ca372d53c2be7d01a1614e71fae1054836
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46306.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46306
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
