# [H] Bluetooth: RFCOMM: hold listener socket in rfcomm_connect_ind()

## Summary
Severity: High
Advisory: CVE-2026-53256
Ecosystem: Linux
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53256
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: RFCOMM: hold listener socket in rfcomm_connect_ind()

rfcomm_get_sock_by_channel() scans rfcomm_sk_list under the list lock,
but returns the selected listener after dropping that lock without
taking a reference. rfcomm_connect_ind() then locks the listener,
queues a child socket on it, and may notify it after unlocking it.

The buggy scenario involves two paths, with each column showing the
order within that path:

rfcomm_connect_ind():            listener close:
  1. Find parent in              1. close() enters
     rfcomm_get_sock_by_channel()   rfcomm_sock_release().
  2. Drop rfcomm_sk_list.lock    2. rfcomm_sock_shutdown()
     without pinning parent.        closes the listener.
  3. Call lock_sock(parent) and  3. rfcomm_sock_kill()
     bt_accept_enqueue(parent,      unlinks and puts parent.
     sk, true).
  4. Read parent flags and may   4. parent can be freed.
     call sk_state_change().

If close wins the race, parent can be freed before
rfcomm_connect_ind() reaches lock_sock(), bt_accept_enqueue(), or the
deferred-setup callback.

Take a reference on the listener before leaving rfcomm_sk_list.lock.
After lock_sock() succeeds, recheck that it is still in BT_LISTEN
before queueing a child, cache the deferred-setup bit while the parent
is locked, and drop the reference after the last parent use.

KASAN reported a slab-use-after-free in lock_sock_nested() from
rfcomm_connect_ind(), with the freeing stack going through
rfcomm_sock_kill() and rfcomm_sock_release().

## References
- https://git.kernel.org/stable/c/1f73f92f66251065a5f39b09a47cf05ea14d3107
- https://git.kernel.org/stable/c/43c441edacf953b39517a44f5e5e10a93618b226
- https://git.kernel.org/stable/c/6f4462d12133106460d7c046b95aad2491e3fddf
- https://git.kernel.org/stable/c/8802413ce63175fb522a2bd609fb043a3550c720
- https://git.kernel.org/stable/c/a07d741c077d4e34b16458241a94d29039386553
- https://git.kernel.org/stable/c/b0e33e409715c617e2a20f46f99aa5403a14dfda
- https://git.kernel.org/stable/c/de31973ef00e5aa55496f84cf6a44bb157a34e02
- https://git.kernel.org/stable/c/f5ec76bdbeb80f75ad0be204371afffee0f8fac8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53256.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53256
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
