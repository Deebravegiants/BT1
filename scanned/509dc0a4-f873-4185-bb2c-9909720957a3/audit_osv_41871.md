# [C] tcp: fix stale per-CPU tcp_tw_isn leak enabling ISN prediction

## Summary
Severity: Critical
Advisory: CVE-2026-64024
Ecosystem: Linux
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64024
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: fix stale per-CPU tcp_tw_isn leak enabling ISN prediction

Blamed commit moved the TIME_WAIT-derived ISN from the skb control
block to a per-CPU variable, assuming the value would always be consumed
by tcp_conn_request() for the same packet that wrote it. That assumption
is violated by multiple drop paths between the producer
(__this_cpu_write(tcp_tw_isn, isn) in tcp_v{4,6}_rcv()) and the consumer
(tcp_conn_request()):

 - min_ttl / min_hopcount check
 - xfrm policy check
 - tcp_inbound_hash() MD5/AO mismatch
 - tcp_filter() eBPF/SO_ATTACH_FILTER drop
 - th->syn && th->fin discard in tcp_rcv_state_process() TCP_LISTEN
 - psp_sk_rx_policy_check() in tcp_v{4,6}_do_rcv()
 - tcp_checksum_complete() in tcp_v{4,6}_do_rcv()
 - tcp_v{4,6}_cookie_check() returning NULL

When a packet is dropped on any of these paths, tcp_tw_isn is left set.

The next SYN processed on the same CPU then consumes the non zero value in
tcp_conn_request(), receiving a potentially predictable ISN.

This patch moves back tcp_tw_isn to skb->cb[], getting rid of the per-cpu
variable.

Note that tcp_v{4,6}_fill_cb() do not set it.

Very litle impact on overall code size/complexity:

$ scripts/bloat-o-meter -t vmlinux.old vmlinux.new
add/remove: 0/0 grow/shrink: 2/1 up/down: 8/-15 (-7)
Function                                     old     new   delta
tcp_v6_rcv                                  3038    3042      +4
tcp_v4_rcv                                  3035    3039      +4
tcp_conn_request                            2938    2923     -15
Total: Before=24436060, After=24436053, chg -0.00%

## References
- https://git.kernel.org/stable/c/1bbf0ced1d9db73ac7893c2187f3459288603e0d
- https://git.kernel.org/stable/c/4affe063fa56c880cbea8d0bfded0bb80751579d
- https://git.kernel.org/stable/c/e47f7060eaf60894e3e4d0e3c4fe6e1f2eacfbdd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64024.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64024
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
