# [H] fs/ntfs3: cancle set bad inode after removing name fails

## Summary
Severity: High
Advisory: CVE-2025-38615
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-38615
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.6.102, >=6.7.0 <6.12.42, >=6.13.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: cancle set bad inode after removing name fails

The reproducer uses a file0 on a ntfs3 file system with a corrupted i_link.
When renaming, the file0's inode is marked as a bad inode because the file
name cannot be deleted.

The underlying bug is that make_bad_inode() is called on a live inode.
In some cases it's "icache lookup finds a normal inode, d_splice_alias()
is called to attach it to dentry, while another thread decides to call
make_bad_inode() on it - that would evict it from icache, but we'd already
found it there earlier".
In some it's outright "we have an inode attached to dentry - that's how we
got it in the first place; let's call make_bad_inode() on it just for shits
and giggles".

## References
- https://git.kernel.org/stable/c/358d4f821c03add421a4c49290538a705852ccf1
- https://git.kernel.org/stable/c/3ed2cc6a6e93fbeb8c0cafce1e7fb1f64a331dcc
- https://git.kernel.org/stable/c/a285395020780adac1ffbc844069c3d700bf007a
- https://git.kernel.org/stable/c/b35a50d639ca5259466ef5fea85529bb4fb17d5b
- https://git.kernel.org/stable/c/d99208b91933fd2a58ed9ed321af07dacd06ddc3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38615.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38615
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
