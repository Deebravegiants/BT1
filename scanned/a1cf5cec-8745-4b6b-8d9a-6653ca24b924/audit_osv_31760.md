# [H] nbd: don't allow reconnect after disconnect

## Summary
Severity: High
Advisory: CVE-2025-21731
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21731
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

nbd: don't allow reconnect after disconnect

Following process can cause nbd_config UAF:

1) grab nbd_config temporarily;

2) nbd_genl_disconnect() flush all recv_work() and release the
initial reference:

  nbd_genl_disconnect
   nbd_disconnect_and_put
    nbd_disconnect
     flush_workqueue(nbd->recv_workq)
    if (test_and_clear_bit(NBD_RT_HAS_CONFIG_REF, ...))
     nbd_config_put
     -> due to step 1), reference is still not zero

3) nbd_genl_reconfigure() queue recv_work() again;

  nbd_genl_reconfigure
   config = nbd_get_config_unlocked(nbd)
   if (!config)
   -> succeed
   if (!test_bit(NBD_RT_BOUND, ...))
   -> succeed
   nbd_reconnect_socket
    queue_work(nbd->recv_workq, &args->work)

4) step 1) release the reference;

5) Finially, recv_work() will trigger UAF:

  recv_work
   nbd_config_put(nbd)
   -> nbd_config is freed
   atomic_dec(&config->recv_threads)
   -> UAF

Fix the problem by clearing NBD_RT_BOUND in nbd_genl_disconnect(), so
that nbd_genl_reconfigure() will fail.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/6bef6222a3f6c7adb6396f77f25a3579d821b09a
- https://git.kernel.org/stable/c/844b8cdc681612ff24df62cdefddeab5772fadf1
- https://git.kernel.org/stable/c/9793bd5ae4bdbdb2dde401a3cab94a6bfd05e302
- https://git.kernel.org/stable/c/a8ee6ecde2b7bfb58c8a3afe8a9d2b848f580739
- https://git.kernel.org/stable/c/d208d2c52b652913b5eefc8ca434b0d6b757f68f
- https://git.kernel.org/stable/c/e3be8862d73cac833e0fb7602636c19c6cb94b11
- https://git.kernel.org/stable/c/e70a578487a47d7cf058904141e586684d1c3381
- https://git.kernel.org/stable/c/e7343fa33751cb07c1c56b666bf37cfca357130e
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21731.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21731
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
