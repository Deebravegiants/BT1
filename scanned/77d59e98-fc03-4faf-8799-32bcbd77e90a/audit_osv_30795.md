# [H] cachefiles: Fix NULL pointer dereference in object->file

## Summary
Severity: High
Advisory: CVE-2024-56549
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56549
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.129, >=6.2.0 <6.6.78, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

cachefiles: Fix NULL pointer dereference in object->file

At present, the object->file has the NULL pointer dereference problem in
ondemand-mode. The root cause is that the allocated fd and object->file
lifetime are inconsistent, and the user-space invocation to anon_fd uses
object->file. Following is the process that triggers the issue:

	  [write fd]				[umount]
cachefiles_ondemand_fd_write_iter
				       fscache_cookie_state_machine
					 cachefiles_withdraw_cookie
  if (!file) return -ENOBUFS
					   cachefiles_clean_up_object
					     cachefiles_unmark_inode_in_use
					     fput(object->file)
					     object->file = NULL
  // file NULL pointer dereference!
  __cachefiles_write(..., file, ...)

Fix this issue by add an additional reference count to the object->file
before write/llseek, and decrement after it finished.

## References
- https://git.kernel.org/stable/c/31ad74b20227ce6b40910ff78b1c604e42975cf1
- https://git.kernel.org/stable/c/785408bbafcfa24c9fc5b251f03fd0780ce182bd
- https://git.kernel.org/stable/c/9582c7664103c9043e80a78f5c382aa6bdd67418
- https://git.kernel.org/stable/c/d6bba3ece960129a553d4b16f1b00c884dc0993a
- https://git.kernel.org/stable/c/f98770440c9bc468e2fd878212ec9526dbe08293
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56549.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56549
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
