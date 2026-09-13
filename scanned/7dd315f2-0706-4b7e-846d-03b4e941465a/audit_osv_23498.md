# [H] fscache: Fix oops due to race with cookie_lru and use_cookie

## Summary
Severity: High
Advisory: CVE-2022-48989
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2022-48989
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

fscache: Fix oops due to race with cookie_lru and use_cookie

If a cookie expires from the LRU and the LRU_DISCARD flag is set, but
the state machine has not run yet, it's possible another thread can call
fscache_use_cookie and begin to use it.

When the cookie_worker finally runs, it will see the LRU_DISCARD flag
set, transition the cookie->state to LRU_DISCARDING, which will then
withdraw the cookie.  Once the cookie is withdrawn the object is removed
the below oops will occur because the object associated with the cookie
is now NULL.

Fix the oops by clearing the LRU_DISCARD bit if another thread uses the
cookie before the cookie_worker runs.

  BUG: kernel NULL pointer dereference, address: 0000000000000008
  ...
  CPU: 31 PID: 44773 Comm: kworker/u130:1 Tainted: G     E    6.0.0-5.dneg.x86_64 #1
  Hardware name: Google Compute Engine/Google Compute Engine, BIOS Google 08/26/2022
  Workqueue: events_unbound netfs_rreq_write_to_cache_work [netfs]
  RIP: 0010:cachefiles_prepare_write+0x28/0x90 [cachefiles]
  ...
  Call Trace:
    netfs_rreq_write_to_cache_work+0x11c/0x320 [netfs]
    process_one_work+0x217/0x3e0
    worker_thread+0x4a/0x3b0
    kthread+0xd6/0x100

## References
- https://git.kernel.org/stable/c/37f0b459c9b67e14fe4dcc3a15d286c4436ed01d
- https://git.kernel.org/stable/c/b5b52de3214a29911f949459a79f6640969b5487
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48989.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48989
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
