# [H] net/smc: fix TOCTOU race between smc_listen_out() and listener close

## Summary
Severity: High
Advisory: CVE-2026-74692
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74692
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/smc: fix TOCTOU race between smc_listen_out() and listener close

smc_listen_out() reads lsmc->sk.sk_state without the listener lock,
then acquires lock_sock_nested() only after the check passes. This
opens a window where smc_close_active() can transition the listener
to SMC_CLOSED, call smc_close_cleanup_listen() to drain the accept
queue, and release the lock, all between the lockless read and the
delayed lock acquisition:

  smc_listen_work (smc_hs_wq)          smc_close_active()
  -------------------------------      -------------------------
  release_sock(child)
  if (sk_state == SMC_LISTEN) TRUE
                                        lock_sock(listener)
                                        sk_state = SMC_CLOSED
                                        smc_close_cleanup_listen()
                                        release_sock(listener)
                                        flush_work(tcp_listen_work)
  lock_sock_nested(listener)
  smc_accept_enqueue(listener, child) /* child enqueued on dead listener */

smc_close_active() flushes only tcp_listen_work. Work items already
dispatched onto smc_hs_wq for the CLC handshake continue running
unguarded. smc_accept_enqueue() takes a sock_hold() on the child that
is never released, so the child smc_sock, its clcsock, and the
reference all leak. A remote peer that opens TCP connections while the
server calls close() can exhaust kernel memory.

Move lock_sock_nested() to before the sk_state check so that the test
and the enqueue are atomic under the listener lock.

## References
- https://git.kernel.org/stable/c/00f89433777236ced4771211047fb5d4cd581cea
- https://git.kernel.org/stable/c/01865e1ddb126b25ac9eba5cdd7ec49e11183a64
- https://git.kernel.org/stable/c/185a4caeecabc150106deda1da170b09f2ad803f
- https://git.kernel.org/stable/c/53c7938d8bcfde3296ec1a347ba2a9393c1fdcfa
- https://git.kernel.org/stable/c/78e5ebcd1c10ed7c8bda0a99e0abd5b62da86d67
- https://git.kernel.org/stable/c/feb71634bb1abab3e8fb5cde874b27001cc1282e
- https://git.kernel.org/stable/c/ff5bcd804b5bc5c64736b7d318c20e12ea9506b8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74692.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74692
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
