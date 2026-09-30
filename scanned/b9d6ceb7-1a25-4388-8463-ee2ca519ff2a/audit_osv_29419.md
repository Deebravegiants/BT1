# [H] landlock: Don't lose track of restrictions on cred_transfer

## Summary
Severity: High
Advisory: CVE-2024-42318
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-42318
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.165, >=5.16.0 <6.1.103, >=6.2.0 <6.6.44, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

landlock: Don't lose track of restrictions on cred_transfer

When a process' cred struct is replaced, this _almost_ always invokes
the cred_prepare LSM hook; but in one special case (when
KEYCTL_SESSION_TO_PARENT updates the parent's credentials), the
cred_transfer LSM hook is used instead.  Landlock only implements the
cred_prepare hook, not cred_transfer, so KEYCTL_SESSION_TO_PARENT causes
all information on Landlock restrictions to be lost.

This basically means that a process with the ability to use the fork()
and keyctl() syscalls can get rid of all Landlock restrictions on
itself.

Fix it by adding a cred_transfer hook that does the same thing as the
existing cred_prepare hook. (Implemented by having hook_cred_prepare()
call hook_cred_transfer() so that the two functions are less likely to
accidentally diverge in the future.)

## References
- http://www.openwall.com/lists/oss-security/2024/08/17/2
- https://bugs.chromium.org/p/project-zero/issues/detail?id=2566
- https://git.kernel.org/stable/c/0d74fd54db0bd0c0c224bef0da8fc95ea9c9f36c
- https://git.kernel.org/stable/c/16896914bace82d7811c62f3b6d5320132384f49
- https://git.kernel.org/stable/c/39705a6c29f8a2b93cf5b99528a55366c50014d1
- https://git.kernel.org/stable/c/916c648323fa53b89eedb34a0988ddaf01406117
- https://git.kernel.org/stable/c/b14cc2cf313bd29056fadbc8ecd7f957cf5791ff
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lore.kernel.org/all/20240817.shahka3Ee1iy@digikod.net/
- https://www.openwall.com/lists/oss-security/2024/08/17/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42318.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42318
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
