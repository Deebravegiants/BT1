# [C] smb: During unmount, ensure all cached dir instances drop their dentry

## Summary
Severity: Critical
Advisory: CVE-2024-53176
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53176
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: During unmount, ensure all cached dir instances drop their dentry

The unmount process (cifs_kill_sb() calling close_all_cached_dirs()) can
race with various cached directory operations, which ultimately results
in dentries not being dropped and these kernel BUGs:

BUG: Dentry ffff88814f37e358{i=1000000000080,n=/}  still in use (2) [unmount of cifs cifs]
VFS: Busy inodes after unmount of cifs (cifs)
------------[ cut here ]------------
kernel BUG at fs/super.c:661!

This happens when a cfid is in the process of being cleaned up when, and
has been removed from the cfids->entries list, including:

- Receiving a lease break from the server
- Server reconnection triggers invalidate_all_cached_dirs(), which
  removes all the cfids from the list
- The laundromat thread decides to expire an old cfid.

To solve these problems, dropping the dentry is done in queued work done
in a newly-added cfid_put_wq workqueue, and close_all_cached_dirs()
flushes that workqueue after it drops all the dentries of which it's
aware. This is a global workqueue (rather than scoped to a mount), but
the queued work is minimal.

The final cleanup work for cleaning up a cfid is performed via work
queued in the serverclose_wq workqueue; this is done separate from
dropping the dentries so that close_all_cached_dirs() doesn't block on
any server operations.

Both of these queued works expect to invoked with a cfid reference and
a tcon reference to avoid those objects from being freed while the work
is ongoing.

While we're here, add proper locking to close_all_cached_dirs(), and
locking around the freeing of cfid->dentry.

## References
- https://git.kernel.org/stable/c/3fa640d035e5ae526769615c35cb9ed4be6e3662
- https://git.kernel.org/stable/c/548812afd96982a76a93ba76c0582ea670c40d9e
- https://git.kernel.org/stable/c/73934e535cffbda1490fa97d82690a0f9aa73e94
- https://git.kernel.org/stable/c/ff4528bbc82d0d90073751f7b49e7b9e9c7e5638
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53176.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53176
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
