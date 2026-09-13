# [H] rxrpc: fix oversized RESPONSE authenticator length check

## Summary
Severity: High
Advisory: CVE-2026-31635
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31635
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.23, >=6.19.0 <6.19.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: fix oversized RESPONSE authenticator length check

rxgk_verify_response() decodes auth_len from the packet and is supposed
to verify that it fits in the remaining bytes. The existing check is
inverted, so oversized RESPONSE authenticators are accepted and passed
to rxgk_decrypt_skb(), which can later reach skb_to_sgvec() with an
impossible length and hit BUG_ON(len).

Decoded from the original latest-net reproduction logs with
scripts/decode_stacktrace.sh:

RIP: __skb_to_sgvec()
  [net/core/skbuff.c:5285 (discriminator 1)]
Call Trace:
 skb_to_sgvec() [net/core/skbuff.c:5305]
 rxgk_decrypt_skb() [net/rxrpc/rxgk_common.h:81]
 rxgk_verify_response() [net/rxrpc/rxgk.c:1268]
 rxrpc_process_connection()
   [net/rxrpc/conn_event.c:266 net/rxrpc/conn_event.c:364
    net/rxrpc/conn_event.c:386]
 process_one_work() [kernel/workqueue.c:3281]
 worker_thread()
   [kernel/workqueue.c:3353 kernel/workqueue.c:3440]
 kthread() [kernel/kthread.c:436]
 ret_from_fork() [arch/x86/kernel/process.c:164]

Reject authenticator lengths that exceed the remaining packet payload.

## References
- https://git.kernel.org/stable/c/a2567217ade970ecc458144b6be469bc015b23e5
- https://git.kernel.org/stable/c/beee051f259acd286fed64c32c2b31e6f5097eb5
- https://git.kernel.org/stable/c/e2f1a80d8b1ed6a5ae585a399c2b46500bdcc305
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31635.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31635
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
- https://github.com/v12-security/pocs/tree/main/dirtydecrypt
