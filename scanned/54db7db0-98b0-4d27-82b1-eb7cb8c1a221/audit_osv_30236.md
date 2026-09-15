# [H] nvmet-auth: assign dh_key to NULL after kfree_sensitive

## Summary
Severity: High
Advisory: CVE-2024-50215
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-09
Source: https://osv.dev/vulnerability/CVE-2024-50215
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.116, >=6.2.0 <6.6.60, >=6.7.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvmet-auth: assign dh_key to NULL after kfree_sensitive

ctrl->dh_key might be used across multiple calls to nvmet_setup_dhgroup()
for the same controller. So it's better to nullify it after release on
error path in order to avoid double free later in nvmet_destroy_auth().

Found by Linux Verification Center (linuxtesting.org) with Svace.

## References
- https://git.kernel.org/stable/c/c60af16e1d6cc2237d58336546d6adfc067b6b8f
- https://git.kernel.org/stable/c/c94e965f766321641ec38e4eece9ce8884543244
- https://git.kernel.org/stable/c/d2f551b1f72b4c508ab9298419f6feadc3b5d791
- https://git.kernel.org/stable/c/e61bd51e44409495d75847e9230736593e4c8710
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50215.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50215
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
