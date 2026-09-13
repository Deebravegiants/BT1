# [H] drm/xe/oa: Fix potential UAF in xe_oa_add_config_ioctl()

## Summary
Severity: High
Advisory: CVE-2025-71099
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-71099
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.64, >=6.13.0 <6.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/oa: Fix potential UAF in xe_oa_add_config_ioctl()

In xe_oa_add_config_ioctl(), we accessed oa_config->id after dropping
metrics_lock. Since this lock protects the lifetime of oa_config, an
attacker could guess the id and call xe_oa_remove_config_ioctl() with
perfect timing, freeing oa_config before we dereference it, leading to
a potential use-after-free.

Fix this by caching the id in a local variable while holding the lock.

v2: (Matt A)
- Dropped mutex_unlock(&oa->metrics_lock) ordering change from
  xe_oa_remove_config_ioctl()

(cherry picked from commit 28aeaed130e8e587fd1b73b6d66ca41ccc5a1a31)

## References
- https://git.kernel.org/stable/c/7cdb9a9da935c687563cc682155461fef5f9b48d
- https://git.kernel.org/stable/c/c6d30b65b7a44dac52ad49513268adbf19eab4a2
- https://git.kernel.org/stable/c/dcb171931954c51a1a7250d558f02b8f36570783
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71099.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71099
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
