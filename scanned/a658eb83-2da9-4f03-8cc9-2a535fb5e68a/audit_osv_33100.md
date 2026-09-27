# [C] ppp: fix race conditions in ppp_fill_forward_path

## Summary
Severity: Critical
Advisory: CVE-2025-39673
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-39673
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.190, >=5.16.0 <6.1.149, >=6.2.0 <6.6.103, >=6.7.0 <6.12.44, >=6.13.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ppp: fix race conditions in ppp_fill_forward_path

ppp_fill_forward_path() has two race conditions:

1. The ppp->channels list can change between list_empty() and
   list_first_entry(), as ppp_lock() is not held. If the only channel
   is deleted in ppp_disconnect_channel(), list_first_entry() may
   access an empty head or a freed entry, and trigger a panic.

2. pch->chan can be NULL. When ppp_unregister_channel() is called,
   pch->chan is set to NULL before pch is removed from ppp->channels.

Fix these by using a lockless RCU approach:
- Use list_first_or_null_rcu() to safely test and access the first list
  entry.
- Convert list modifications on ppp->channels to their RCU variants and
  add synchronize_net() after removal.
- Check for a NULL pch->chan before dereferencing it.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/0417adf367a0af11adf7ace849af4638cfb573f7
- https://git.kernel.org/stable/c/0f1630be6fcca3f0c63e4b242ad202e5cde28a40
- https://git.kernel.org/stable/c/94731cc551e29511d85aa8dec61a6c071b1f2430
- https://git.kernel.org/stable/c/9a1969fbffc1f1900d92d7594b1b7d8d72ef3dc7
- https://git.kernel.org/stable/c/ca18d751bcc9faf5b7e82e9fae1223d103928181
- https://git.kernel.org/stable/c/f97f6475fdcb3c28ff3c55cc4b7bde632119ec08
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39673.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39673
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
