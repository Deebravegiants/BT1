# [H] bpf, sockmap: Fix skb refcnt race after locking changes

## Summary
Severity: High
Advisory: CVE-2023-53836
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2023-53836
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.189, >=5.16.0 <6.1.54, >=6.2.0 <6.5.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf, sockmap: Fix skb refcnt race after locking changes

There is a race where skb's from the sk_psock_backlog can be referenced
after userspace side has already skb_consumed() the sk_buff and its refcnt
dropped to zer0 causing use after free.

The flow is the following:

  while ((skb = skb_peek(&psock->ingress_skb))
    sk_psock_handle_Skb(psock, skb, ..., ingress)
    if (!ingress) ...
    sk_psock_skb_ingress
       sk_psock_skb_ingress_enqueue(skb)
          msg->skb = skb
          sk_psock_queue_msg(psock, msg)
    skb_dequeue(&psock->ingress_skb)

The sk_psock_queue_msg() puts the msg on the ingress_msg queue. This is
what the application reads when recvmsg() is called. An application can
read this anytime after the msg is placed on the queue. The recvmsg hook
will also read msg->skb and then after user space reads the msg will call
consume_skb(skb) on it effectively free'ing it.

But, the race is in above where backlog queue still has a reference to
the skb and calls skb_dequeue(). If the skb_dequeue happens after the
user reads and free's the skb we have a use after free.

The !ingress case does not suffer from this problem because it uses
sendmsg_*(sk, msg) which does not pass the sk_buff further down the
stack.

The following splat was observed with 'test_progs -t sockmap_listen':

  [ 1022.710250][ T2556] general protection fault, ...
  [...]
  [ 1022.712830][ T2556] Workqueue: events sk_psock_backlog
  [ 1022.713262][ T2556] RIP: 0010:skb_dequeue+0x4c/0x80
  [ 1022.713653][ T2556] Code: ...
  [...]
  [ 1022.720699][ T2556] Call Trace:
  [ 1022.720984][ T2556]  <TASK>
  [ 1022.721254][ T2556]  ? die_addr+0x32/0x80^M
  [ 1022.721589][ T2556]  ? exc_general_protection+0x25a/0x4b0
  [ 1022.722026][ T2556]  ? asm_exc_general_protection+0x22/0x30
  [ 1022.722489][ T2556]  ? skb_dequeue+0x4c/0x80
  [ 1022.722854][ T2556]  sk_psock_backlog+0x27a/0x300
  [ 1022.723243][ T2556]  process_one_work+0x2a7/0x5b0
  [ 1022.723633][ T2556]  worker_thread+0x4f/0x3a0
  [ 1022.723998][ T2556]  ? __pfx_worker_thread+0x10/0x10
  [ 1022.724386][ T2556]  kthread+0xfd/0x130
  [ 1022.724709][ T2556]  ? __pfx_kthread+0x10/0x10
  [ 1022.725066][ T2556]  ret_from_fork+0x2d/0x50
  [ 1022.725409][ T2556]  ? __pfx_kthread+0x10/0x10
  [ 1022.725799][ T2556]  ret_from_fork_asm+0x1b/0x30
  [ 1022.726201][ T2556]  </TASK>

To fix we add an skb_get() before passing the skb to be enqueued in the
engress queue. This bumps the skb->users refcnt so that consume_skb()
and kfree_skb will not immediately free the sk_buff. With this we can
be sure the skb is still around when we do the dequeue. Then we just
need to decrement the refcnt or free the skb in the backlog case which
we do by calling kfree_skb() on the ingress case as well as the sendmsg
case.

Before locking change from fixes tag we had the sock locked so we
couldn't race with user and there was no issue here.

## References
- https://git.kernel.org/stable/c/65ad600b9bde68d2d28709943ab00b51ca8f0a1d
- https://git.kernel.org/stable/c/923877254f002ae87d441382bb1096d9e773d56d
- https://git.kernel.org/stable/c/a454d84ee20baf7bd7be90721b9821f73c7d23d9
- https://git.kernel.org/stable/c/e6b5e47adb9166e732cdf7e6e034946e3f89f36d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53836.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53836
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
