# [C] bpf, skmsg: fix verdict sk_data_ready racing with ktls rx

## Summary
Severity: Critical
Advisory: CVE-2026-64025
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64025
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf, skmsg: fix verdict sk_data_ready racing with ktls rx

sk_psock_strp_data_ready() already checks tls_sw_has_ctx_rx() and
defers to psock->saved_data_ready when a TLS RX context is present,
avoiding a conflict with the TLS strparser's ownership of the receive
queue (commit e91de6afa81c, "bpf: Fix running sk_skb program types
with ktls").

sk_psock_verdict_data_ready() has no equivalent guard.  When a socket
is inserted into a sockmap (BPF_SK_SKB_VERDICT) before TLS RX is
configured, tls_sw_strparser_arm() saves sk_psock_verdict_data_ready
as rx_ctx->saved_data_ready.  On data arrival:

  tls_data_ready -> tls_strp_data_ready -> tls_rx_msg_ready
    -> saved_data_ready() = sk_psock_verdict_data_ready()
      -> tcp_read_skb() drains sk_receive_queue via __skb_unlink()
         without calling tcp_eat_skb(), so copied_seq is not advanced.

tls_strp_msg_load() then finds tcp_inq() >= full_len (stale), calls
tcp_recv_skb() on the now-empty queue, hits WARN_ON_ONCE(!first), and
returns with rx_ctx->strp.anchor.frag_list pointing at a psock-owned
(potentially freed) skb.  tls_decrypt_sg() subsequently walks that
frag_list: use-after-free.

Apply the same fix as sk_psock_strp_data_ready(): if a TLS RX context
is present, call psock->saved_data_ready (sock_def_readable) to wake
recv() waiters and return immediately, leaving the receive queue
untouched.  TLS retains sole ownership of the queue and decrypts the
record normally through tls_sw_recvmsg().

## References
- https://git.kernel.org/stable/c/1861d369efd62d67796563bf3e01fc22e5626f8b
- https://git.kernel.org/stable/c/7c8cf21bc4efb4af18d6096db3f8bd06d622251c
- https://git.kernel.org/stable/c/8a52139560f833c3975032e1f5762611e3a36d71
- https://git.kernel.org/stable/c/c9ea01768903ae47f210cd457af1dead6de7a9c3
- https://git.kernel.org/stable/c/ddf8029623a1af20e984c040e89ff918158397ab
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64025.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64025
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
