# [H] ipmi: Fix user refcount underflow in event delivery

## Summary
Severity: High
Advisory: CVE-2026-72042
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72042
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipmi: Fix user refcount underflow in event delivery

ipmi_alloc_recv_msg(user) takes the temporary user reference owned by the
receive message, and ipmi_free_recv_msg() drops it again. If event delivery
fails after allocating receive messages for earlier users,
handle_read_event_rsp() rolls those messages back with
ipmi_free_recv_msg().

That rollback path still drops user->refcount explicitly after freeing each
message. The extra put can free a user that remains linked on intf->users,
so later event delivery may dereference a freed user or trip refcount_t's
addition-on-zero warning when ipmi_alloc_recv_msg() tries to acquire
another reference.

Remove the stale explicit put and the now-dead user assignment. Keep the
list_del() and ipmi_free_recv_msg() calls; they are the required rollback
operations.

## References
- https://git.kernel.org/stable/c/6aa9e61c46465d231e9beddf56af7effd71be682
- https://git.kernel.org/stable/c/7be349d4fcc5e065295b83418a22d27a68afbdb6
- https://git.kernel.org/stable/c/ddbb6e3dc9bb4743de686aa1598c31e745cee76b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72042.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72042
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
