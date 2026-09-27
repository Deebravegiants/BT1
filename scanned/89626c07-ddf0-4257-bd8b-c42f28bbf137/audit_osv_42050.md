# [H] smb: client: resolve SWN tcon from live registrations

## Summary
Severity: High
Advisory: CVE-2026-64401
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64401
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: resolve SWN tcon from live registrations

cifs_swn_notify() looks up a witness registration by id under
cifs_swnreg_idr_mutex, drops the mutex, and then uses the registration's
cached tcon pointer.  That pointer is not a lifetime reference, and it is
not a stable representative once cifs_get_swn_reg() lets multiple tcons
for the same net/share name share one registration id.

A same-share second mount can keep the cifs_swn_reg alive after the first
tcon unregisters and is freed.  The registration then still points at the
freed first tcon, so taking tc_lock or incrementing tc_count through
swnreg->tcon only moves the use-after-free earlier.  Taking tc_lock while
holding cifs_swnreg_idr_mutex also violates the documented CIFS lock
order.

Fix this by making the registration store only the stable witness
identity: id, net name, share name, and notify flags.  When a notify
arrives, copy that identity under cifs_swnreg_idr_mutex, drop the mutex,
then find and pin a live witness tcon that currently matches the net/share
pair under the normal cifs_tcp_ses_lock -> tc_lock order.  The notification
path uses that pinned tcon directly and drops the reference when done.

Registration and unregister messages now use the live tcon passed by the
caller instead of a cached tcon in the registration.  The final unregister
send is folded into cifs_swn_unregister() while the registration is still
protected by cifs_swnreg_idr_mutex.  This removes the previous
find/drop/reacquire raw-pointer window.  The release path only removes the
idr entry and frees the stable identity strings.

This preserves the intended one-registration/many-tcon behavior: a
registration id represents a net/share pair, and notify handling acts on a
live representative selected at use time.  It also preserves CLIENT_MOVE
ordering for the representative tcon because the old-IP unregister is sent
before cifs_swn_register() sends the new-IP register.

## References
- https://git.kernel.org/stable/c/0700f946659d0ab2352ec8a9b1c6fc74b13a27d7
- https://git.kernel.org/stable/c/51d18db392e5386a7bb9e816d611f14e600cca3c
- https://git.kernel.org/stable/c/91b8a58c6ac15c7db6518f696389933282f88da7
- https://git.kernel.org/stable/c/945b4a4a54497db1dcb2f20ef801a84e884dac21
- https://git.kernel.org/stable/c/aa3c0cab4b28c5007ec570c63e1d6ad6943ed0fd
- https://git.kernel.org/stable/c/ec457f9afe5ae9538bdcd58fd4cb442b9787e183
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64401.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64401
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
