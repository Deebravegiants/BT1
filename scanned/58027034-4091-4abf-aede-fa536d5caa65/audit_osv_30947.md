# [M] drm/sti: avoid potential dereference of error pointers

## Summary
Severity: Medium
Advisory: CVE-2024-56776
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-08
Source: https://osv.dev/vulnerability/CVE-2024-56776
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.12.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/sti: avoid potential dereference of error pointers

The return value of drm_atomic_get_crtc_state() needs to be
checked. To avoid use of error pointer 'crtc_state' in case
of the failure.

## References
- https://git.kernel.org/stable/c/40725c5fabee804fecce41d4d5c5bae80c45e1c4
- https://git.kernel.org/stable/c/831214f77037de02afc287eae93ce97f218d8c04
- https://git.kernel.org/stable/c/8ab73ac97c0fa528f66eeccd9bb53eb6eb7d20dc
- https://git.kernel.org/stable/c/e98ff67f5a68114804607de549c2350d27628fc7
- https://git.kernel.org/stable/c/f67786293193cf01ebcc6fdbcbd1587b24f52679
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56776.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56776
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
