# [H] sctp: properly validate chunk size in sctp_sf_ootb()

## Summary
Severity: High
Advisory: CVE-2024-50299
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50299
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.19.324, >=4.20.0 <5.4.286, >=5.5.0 <5.10.230, >=5.11.0 <5.15.172, >=5.16.0 <6.1.117, >=6.2.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: properly validate chunk size in sctp_sf_ootb()

A size validation fix similar to that in Commit 50619dbf8db7 ("sctp: add
size validation when walking chunks") is also required in sctp_sf_ootb()
to address a crash reported by syzbot:

  BUG: KMSAN: uninit-value in sctp_sf_ootb+0x7f5/0xce0 net/sctp/sm_statefuns.c:3712
  sctp_sf_ootb+0x7f5/0xce0 net/sctp/sm_statefuns.c:3712
  sctp_do_sm+0x181/0x93d0 net/sctp/sm_sideeffect.c:1166
  sctp_endpoint_bh_rcv+0xc38/0xf90 net/sctp/endpointola.c:407
  sctp_inq_push+0x2ef/0x380 net/sctp/inqueue.c:88
  sctp_rcv+0x3831/0x3b20 net/sctp/input.c:243
  sctp4_rcv+0x42/0x50 net/sctp/protocol.c:1159
  ip_protocol_deliver_rcu+0xb51/0x13d0 net/ipv4/ip_input.c:205
  ip_local_deliver_finish+0x336/0x500 net/ipv4/ip_input.c:233

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://cert-portal.siemens.com/productcert/html/ssa-398330.html
- https://git.kernel.org/stable/c/0ead60804b64f5bd6999eec88e503c6a1a242d41
- https://git.kernel.org/stable/c/40b283ba76665437bc2ac72079c51b57b25bff9e
- https://git.kernel.org/stable/c/67b9a278b80f71ec62091ded97c6bcbea33b5ec3
- https://git.kernel.org/stable/c/8820d2d6589f62ee5514793fff9b50c9f8101182
- https://git.kernel.org/stable/c/9b5d42aeaf1a52f73b003a33da6deef7df34685f
- https://git.kernel.org/stable/c/a758aa6a773bb872196bcc3173171ef8996bddf0
- https://git.kernel.org/stable/c/bf9bff13225baf5f658577f7d985fc4933d79527
- https://git.kernel.org/stable/c/d3fb3cc83cf313e4f87063ce0f3fea76b071567b
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50299.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50299
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
