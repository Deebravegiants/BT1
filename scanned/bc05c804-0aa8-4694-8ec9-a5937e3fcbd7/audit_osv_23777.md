# [H] Bluetooth: fix dangling sco_conn and use-after-free in sco_sock_timeout

## Summary
Severity: High
Advisory: CVE-2022-49474
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49474
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.15.0 <5.17.14, >=5.16.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: fix dangling sco_conn and use-after-free in sco_sock_timeout

Connecting the same socket twice consecutively in sco_sock_connect()
could lead to a race condition where two sco_conn objects are created
but only one is associated with the socket. If the socket is closed
before the SCO connection is established, the timer associated with the
dangling sco_conn object won't be canceled. As the sock object is being
freed, the use-after-free problem happens when the timer callback
function sco_sock_timeout() accesses the socket. Here's the call trace:

dump_stack+0x107/0x163
? refcount_inc+0x1c/
print_address_description.constprop.0+0x1c/0x47e
? refcount_inc+0x1c/0x7b
kasan_report+0x13a/0x173
? refcount_inc+0x1c/0x7b
check_memory_region+0x132/0x139
refcount_inc+0x1c/0x7b
sco_sock_timeout+0xb2/0x1ba
process_one_work+0x739/0xbd1
? cancel_delayed_work+0x13f/0x13f
? __raw_spin_lock_init+0xf0/0xf0
? to_kthread+0x59/0x85
worker_thread+0x593/0x70e
kthread+0x346/0x35a
? drain_workqueue+0x31a/0x31a
? kthread_bind+0x4b/0x4b
ret_from_fork+0x1f/0x30

## References
- https://git.kernel.org/stable/c/36c644c63bfcaee2d3a426f45e89a9cd09799318
- https://git.kernel.org/stable/c/390d82733a953c1fabf3de9c9618091a7a9c90a6
- https://git.kernel.org/stable/c/537f619dea4e3fa8ed1f8f938abffe3615794bcc
- https://git.kernel.org/stable/c/65d347cb39e2e6bd0c2a745ad7c928998ebb0162
- https://git.kernel.org/stable/c/6f55fac0af3531cf60d11369454c41f5fc81ab3f
- https://git.kernel.org/stable/c/7aa1e7d15f8a5b65f67bacb100d8fc033b21efa2
- https://git.kernel.org/stable/c/7d61dbd7311ab978d8ddac1749a758de4de00374
- https://git.kernel.org/stable/c/99df16007f4bbf9abfc3478cb17d10f0d7f8906e
- https://git.kernel.org/stable/c/9de3dc09e56f8deacd2bdbf4cecb71e11a312405
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49474.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49474
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
