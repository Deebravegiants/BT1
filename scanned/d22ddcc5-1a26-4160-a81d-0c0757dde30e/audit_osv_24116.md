# [H] NFSD: fix use-after-free on source server when doing inter-server copy

## Summary
Severity: High
Advisory: CVE-2022-50241
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2022-50241
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.150, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: fix use-after-free on source server when doing inter-server copy

Use-after-free occurred when the laundromat tried to free expired
cpntf_state entry on the s2s_cp_stateids list after inter-server
copy completed. The sc_cp_list that the expired copy state was
inserted on was already freed.

When COPY completes, the Linux client normally sends LOCKU(lock_state x),
FREE_STATEID(lock_state x) and CLOSE(open_state y) to the source server.
The nfs4_put_stid call from nfsd4_free_stateid cleans up the copy state
from the s2s_cp_stateids list before freeing the lock state's stid.

However, sometimes the CLOSE was sent before the FREE_STATEID request.
When this happens, the nfsd4_close_open_stateid call from nfsd4_close
frees all lock states on its st_locks list without cleaning up the copy
state on the sc_cp_list list. When the time the FREE_STATEID arrives the
server returns BAD_STATEID since the lock state was freed. This causes
the use-after-free error to occur when the laundromat tries to free
the expired cpntf_state.

This patch adds a call to nfs4_free_cpntf_statelist in
nfsd4_close_open_stateid to clean up the copy state before calling
free_ol_stateid_reaplist to free the lock state's stid on the reaplist.

## References
- https://git.kernel.org/stable/c/019805fea91599b22dfa62ffb29c022f35abeb06
- https://git.kernel.org/stable/c/35aa0fb8c3033a3d78603356e96fc18c5b9cceb2
- https://git.kernel.org/stable/c/6ea71246b7a02af675d733e72d14bd0d591d5f4a
- https://git.kernel.org/stable/c/83b94969751a691347606dbe6b1865efcfa5a643
- https://git.kernel.org/stable/c/bbacfcde5fff25ac22597e8373a065c647da6738
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50241.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50241
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
