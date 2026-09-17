# [H] drm/panfrost: Fix shrinker list corruption by madvise IOCTL

## Summary
Severity: High
Advisory: CVE-2022-49645
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49645
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.4.207, >=5.5.0 <5.10.132, >=5.11.0 <5.15.56, >=5.16.0 <5.18.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/panfrost: Fix shrinker list corruption by madvise IOCTL

Calling madvise IOCTL twice on BO causes memory shrinker list corruption
and crashes kernel because BO is already on the list and it's added to
the list again, while BO should be removed from the list before it's
re-added. Fix it.

## References
- https://git.kernel.org/stable/c/0581613df7f9a4c5fac096ce1d5fb15b7b994240
- https://git.kernel.org/stable/c/1807d8867402a58b831a7fc16832747ff559a0d1
- https://git.kernel.org/stable/c/393594aad55179eb761af41533d8d1d6eb4543b0
- https://git.kernel.org/stable/c/9fc33eaaa979d112d10fea729edcd2a2e21aa912
- https://git.kernel.org/stable/c/f036392edd9c49090781d8cca26ad6557a63bae4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49645.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49645
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
