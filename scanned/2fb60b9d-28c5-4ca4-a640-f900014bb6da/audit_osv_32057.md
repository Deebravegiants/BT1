# [M] ALSA: timer: Don't take register_mutex with copy_from/to_user()

## Summary
Severity: Medium
Advisory: CVE-2025-23134
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-23134
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: timer: Don't take register_mutex with copy_from/to_user()

The infamous mmap_lock taken in copy_from/to_user() can be often
problematic when it's called inside another mutex, as they might lead
to deadlocks.

In the case of ALSA timer code, the bad pattern is with
guard(mutex)(&register_mutex) that covers copy_from/to_user() -- which
was mistakenly introduced at converting to guard(), and it had been
carefully worked around in the past.

This patch fixes those pieces simply by moving copy_from/to_user() out
of the register mutex lock again.

## References
- https://git.kernel.org/stable/c/15291b561d8cc835a2eea76b394070cf8e072771
- https://git.kernel.org/stable/c/296f7a9e15aab276db11206cbc1e2ae1215d7862
- https://git.kernel.org/stable/c/3424c8f53bc63c87712a7fc22dc13d0cc85fb0d6
- https://git.kernel.org/stable/c/b074f47e55df93832bbbca1b524c501e6fea1c0d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/23xxx/CVE-2025-23134.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-23134
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
