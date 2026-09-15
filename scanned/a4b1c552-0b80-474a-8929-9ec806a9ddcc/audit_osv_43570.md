# [C] dlm: fix add msg handle in send_queue ordered

## Summary
Severity: Critical
Advisory: CVE-2026-74401
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74401
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

dlm: fix add msg handle in send_queue ordered

In a benchmark scenario triggering a lot of requests that triggers a lot
of DLM messages on the network it can be that the mh->seq is not ordered
according the oldest seq number. This ordering is required by
dlm_receive_ack as "before(mh->seq, seq)" will stop to check for older
sequence numbers that are ordered in the tail of "node->send_queue".

The side effects of not having it correct ordered regarding
"before(mh->seq, seq)" are refcounting issues and use-after free.

I only was able to reproduce this issue in a experimental DLM branch
and a user space DLM benchmark that uses io_uring. After changing this I
don't experienced any refcounting with the sending buffer issues anymore.

## References
- https://git.kernel.org/stable/c/4d45250b1d22960f86d83245be188b16e456218b
- https://git.kernel.org/stable/c/6369619f1b665f12d8c99cc6ff733c64eb08b22e
- https://git.kernel.org/stable/c/712714f818d83373847874ab0f8e426be79296cf
- https://git.kernel.org/stable/c/ae9e534e502a0f48c12baf83608c5de0ff0eab11
- https://git.kernel.org/stable/c/d2248cb70c070f8f04762872772e155b59016f17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74401.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74401
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
