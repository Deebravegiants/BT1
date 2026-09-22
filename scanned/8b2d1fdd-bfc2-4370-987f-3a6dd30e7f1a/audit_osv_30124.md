# [H] btrfs: fix uninitialized pointer free in add_inode_ref()

## Summary
Severity: High
Advisory: CVE-2024-50088
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-29
Source: https://osv.dev/vulnerability/CVE-2024-50088
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.114, >=6.2.0 <6.11.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: fix uninitialized pointer free in add_inode_ref()

The add_inode_ref() function does not initialize the "name" struct when
it is declared.  If any of the following calls to "read_one_inode()
returns NULL,

	dir = read_one_inode(root, parent_objectid);
	if (!dir) {
		ret = -ENOENT;
		goto out;
	}

	inode = read_one_inode(root, inode_objectid);
	if (!inode) {
		ret = -EIO;
		goto out;
	}

then "name.name" would be freed on "out" before being initialized.

out:
	...
	kfree(name.name);

This issue was reported by Coverity with CID 1526744.

## References
- https://git.kernel.org/stable/c/12cf028381aa19bc38465341512c280256e8d82d
- https://git.kernel.org/stable/c/66691c6e2f18d2aa4b22ffb624b9bdc97e9979e4
- https://git.kernel.org/stable/c/a941f3d5b1469c60a7e70e775584f110b47e0d16
- https://git.kernel.org/stable/c/e11ce03b58743bf1e096c48fcaa7e6f08eb75dfa
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50088.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50088
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
