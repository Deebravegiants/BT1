# [H] fscrypt: use the mount idmap for the owner check in fscrypt_ioctl_set_policy()

## Summary
Severity: High
Advisory: CVE-2026-74595
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74595
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

fscrypt: use the mount idmap for the owner check in fscrypt_ioctl_set_policy()

fscrypt_ioctl_set_policy() calls inode_owner_or_capable() with
&nop_mnt_idmap before allowing an encryption policy to be set, instead
of the idmap of the mount the ioctl was issued on.

fscrypt is used by filesystems that support idmapped mounts (e.g. ext4,
f2fs), so on such a mount this compares the caller's fsuid against the
unmapped on-disk owner rather than the mapped owner: the actual owner
can be wrongly denied with -EACCES and an unrelated caller wrongly
allowed.  Use file_mnt_idmap(filp) instead.

## References
- https://git.kernel.org/stable/c/0baeb730044981f5ec5fb7d62a3763835ea606f6
- https://git.kernel.org/stable/c/174633a468817a49bd474bcfc9067c84e54efe68
- https://git.kernel.org/stable/c/33b7e810ce09955aa02f3b632455cf5e7ac990a9
- https://git.kernel.org/stable/c/653e888a24c87b8bbeab44d7e558a1c1a3641088
- https://git.kernel.org/stable/c/6a67c460b12315033268dce597546984fe5739e7
- https://git.kernel.org/stable/c/98516ba8b817f34e86bdd7a5b7a383cff75c3ddf
- https://git.kernel.org/stable/c/cf6c993c0feca7984797e634deba3c80342e199a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74595.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74595
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
