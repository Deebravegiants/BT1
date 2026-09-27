# [C] smb: client: fix use-after-free of signing key

## Summary
Severity: Critical
Advisory: CVE-2024-53179
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53179
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.12.0 <6.6.70, >=6.7.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix use-after-free of signing key

Customers have reported use-after-free in @ses->auth_key.response with
SMB2.1 + sign mounts which occurs due to following race:

task A                         task B
cifs_mount()
 dfs_mount_share()
  get_session()
   cifs_mount_get_session()    cifs_send_recv()
    cifs_get_smb_ses()          compound_send_recv()
     cifs_setup_session()        smb2_setup_request()
      kfree_sensitive()           smb2_calc_signature()
                                   crypto_shash_setkey() *UAF*

Fix this by ensuring that we have a valid @ses->auth_key.response by
checking whether @ses->ses_status is SES_GOOD or SES_EXITING with
@ses->ses_lock held.  After commit 24a9799aa8ef ("smb: client: fix UAF
in smb2_reconnect_server()"), we made sure to call ->logoff() only
when @ses was known to be good (e.g. valid ->auth_key.response), so
it's safe to access signing key when @ses->ses_status == SES_EXITING.

## References
- https://git.kernel.org/stable/c/0e2b654a3848bf9da3b0d54c1ccf3f1b8c635591
- https://git.kernel.org/stable/c/343d7fe6df9e247671440a932b6a73af4fa86d95
- https://git.kernel.org/stable/c/39619c65ab4bbb3e78c818f537687653e112764d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53179.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53179
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
