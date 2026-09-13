# [H] Bluetooth: ISO: serialize iso_sock_clear_timer with socket lock

## Summary
Severity: High
Advisory: CVE-2026-63945
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63945
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: ISO: serialize iso_sock_clear_timer with socket lock

iso_sock_close() calls iso_sock_clear_timer() before acquiring
lock_sock(sk).

iso_sock_clear_timer() reads iso_pi(sk)->conn twice without the
socket lock held:

    if (!iso_pi(sk)->conn)
        return;
    cancel_delayed_work(&iso_pi(sk)->conn->timeout_work);

Concurrently, iso_conn_del() executes under lock_sock(sk) and calls
iso_chan_del(), which sets iso_pi(sk)->conn to NULL and may result in
the final reference to the connection being dropped:

    CPU0                         CPU1
    ----                         ----
    iso_sock_clear_timer()
      if (conn != NULL) ...      lock_sock(sk)
                                   iso_chan_del()
                                   iso_pi(sk)->conn = NULL
      cancel_delayed_work(conn)  /* NULL deref or UAF */

iso_pi(sk)->conn is not stable across the unlock window, causing a
NULL pointer dereference or use-after-free.

Serialize iso_sock_clear_timer() with the socket lock by moving it
inside lock_sock()/release_sock(), matching the pattern used in
iso_conn_del() and all other call sites.

## References
- https://git.kernel.org/stable/c/35f68f36d9883d56dec21cf85f7556d4657fc393
- https://git.kernel.org/stable/c/4b5f8e608749b7e8fa386c6e4301cf9272595859
- https://git.kernel.org/stable/c/51cb9dcfdf9a1bccf312ab2ae4b62db629f7dcd5
- https://git.kernel.org/stable/c/996c2104d0726a8fe584f85b3d6327197374a348
- https://git.kernel.org/stable/c/bc08c15746f25f41dd0508b25780d1e84acbb2ef
- https://git.kernel.org/stable/c/d9cbf7144ec589a3f0cc91f74a1a1af2d2b14afa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63945.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63945
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
