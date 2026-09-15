# [H] net: rds: don't hold sock lock when cancelling work from rds_tcp_reset_callbacks()

## Summary
Severity: High
Advisory: CVE-2022-50676
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2022-50676
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <4.9.331, >=4.10.0 <4.14.296, >=4.15.0 <4.19.262, >=4.20.0 <5.4.220, >=5.5.0 <5.10.150, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: rds: don't hold sock lock when cancelling work from rds_tcp_reset_callbacks()

syzbot is reporting lockdep warning at rds_tcp_reset_callbacks() [1], for
commit ac3615e7f3cffe2a ("RDS: TCP: Reduce code duplication in
rds_tcp_reset_callbacks()") added cancel_delayed_work_sync() into a section
protected by lock_sock() without realizing that rds_send_xmit() might call
lock_sock().

We don't need to protect cancel_delayed_work_sync() using lock_sock(), for
even if rds_{send,recv}_worker() re-queued this work while __flush_work()
 from cancel_delayed_work_sync() was waiting for this work to complete,
retried rds_{send,recv}_worker() is no-op due to the absence of RDS_CONN_UP
bit.

## References
- https://git.kernel.org/stable/c/2425007c0967a7c04b0dee7cce05ecf0ca869ad1
- https://git.kernel.org/stable/c/30bfa5aa7228eb1e67663d67e553627e572cc717
- https://git.kernel.org/stable/c/360aa7219285fac63dab99706a16f2daf3222abe
- https://git.kernel.org/stable/c/5d2ba255e93211e541373469dffbda7c99dfa0e5
- https://git.kernel.org/stable/c/a91b750fd6629354460282bbf5146c01b05c4859
- https://git.kernel.org/stable/c/afe7053c390fe8ff27d0c2ceaece5625283044ba
- https://git.kernel.org/stable/c/c380c28ab9b15fc53565909c814f6dd3e7f77c4b
- https://git.kernel.org/stable/c/da349221c4d2d4ac5f606c1c3b36d4ef0b3e6a0c
- https://git.kernel.org/stable/c/e3cb25d3ad08f5dbd53ce2b31720cad529944322
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50676.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50676
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
