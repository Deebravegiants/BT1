# [H] net/iucv: take a reference on the socket found in afiucv_hs_rcv()

## Summary
Severity: High
Advisory: CVE-2026-68397
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68397
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.2.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/iucv: take a reference on the socket found in afiucv_hs_rcv()

afiucv_hs_rcv() looks up the destination socket under iucv_sk_list.lock,
drops the lock, and then passes the socket to the afiucv_hs_callback_*()
handlers without holding a reference. AF_IUCV sockets are not
RCU-protected and are freed synchronously by iucv_sock_kill() ->
sock_put(), so a concurrent close can free the socket in the window
between read_unlock() and the handler, which then dereferences freed
memory (for example sk->sk_data_ready() in afiucv_hs_callback_syn()).

Take a reference with sock_hold() while the socket is still on the list
and release it with sock_put() once the handler has run.

## References
- https://git.kernel.org/stable/c/1801cb20a5025a787d6853e19c38db138344b4b4
- https://git.kernel.org/stable/c/4dc0e63abf8bc7ba8892e617c1fb8b204361e022
- https://git.kernel.org/stable/c/4fa349156043dc119721d067329714179f501749
- https://git.kernel.org/stable/c/5595ea59cdf29182cf6a270cacc1426c57b603de
- https://git.kernel.org/stable/c/5739be5c19495d709d902a2912c9102ce78740d5
- https://git.kernel.org/stable/c/bc6c6e546ffff8865daaeb622ef348c2d481e80f
- https://git.kernel.org/stable/c/c75a950e77356e526672cba4584080c6c8b793b6
- https://git.kernel.org/stable/c/e3e0679fc950191aff8f27fa78abcfc2462cff4a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68397.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68397
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
