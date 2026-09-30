# [M] rapidio: fix possible name leaks when rio_add_device() fails

## Summary
Severity: Medium
Advisory: CVE-2022-50343
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2022-50343
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <4.9.337, >=4.10.0 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

rapidio: fix possible name leaks when rio_add_device() fails

Patch series "rapidio: fix three possible memory leaks".

This patchset fixes three name leaks in error handling.
 - patch #1 fixes two name leaks while rio_add_device() fails.
 - patch #2 fixes a name leak while  rio_register_mport() fails.


This patch (of 2):

If rio_add_device() returns error, the name allocated by dev_set_name()
need be freed.  It should use put_device() to give up the reference in the
error path, so that the name can be freed in kobject_cleanup(), and the
'rdev' can be freed in rio_release_dev().

## References
- https://git.kernel.org/stable/c/3b4676f274a6b5d001176f15d0542100bbf4b59a
- https://git.kernel.org/stable/c/440afd7fd9b164fdde6fc9da8c47d3d7f20dcce8
- https://git.kernel.org/stable/c/80fad2e53eaed2b3a2ff596575f65669e13ceda5
- https://git.kernel.org/stable/c/85fbf58b15c09d3a6a03098c1e42ebfe9002f39d
- https://git.kernel.org/stable/c/88fa351b20ca300693a206ccd3c4b0e0647944d8
- https://git.kernel.org/stable/c/c413f65011ff8caffabcde0e1c3ceede48a48d6f
- https://git.kernel.org/stable/c/c482cb0deb57924335103fe592c379a076d867f8
- https://git.kernel.org/stable/c/ec3f04f74f50d0b6bac04d795c93c2b852753a7a
- https://git.kernel.org/stable/c/f9574cd48679926e2a569e1957a5a1bcc8a719ac
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50343.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50343
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
