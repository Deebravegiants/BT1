# [H] drm/vmwgfx: Fix invalid reads in fence signaled events

## Summary
Severity: High
Advisory: CVE-2024-36960
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-06-03
Source: https://osv.dev/vulnerability/CVE-2024-36960
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.4.0 <4.19.314, >=4.20.0 <5.4.276, >=5.5.0 <5.10.217, >=5.11.0 <5.15.159, >=5.16.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/vmwgfx: Fix invalid reads in fence signaled events

Correctly set the length of the drm_event to the size of the structure
that's actually used.

The length of the drm_event was set to the parent structure instead of
to the drm_vmw_event_fence which is supposed to be read. drm_read
uses the length parameter to copy the event to the user space thus
resuling in oob reads.

## References
- https://git.kernel.org/stable/c/0dbfc73670b357456196130551e586345ca48e1b
- https://git.kernel.org/stable/c/2f527e3efd37c7c5e85e8aa86308856b619fa59f
- https://git.kernel.org/stable/c/3cd682357c6167f636aec8ac0efaa8ba61144d36
- https://git.kernel.org/stable/c/7b5fd3af4a250dd0a2a558e07b43478748eb5d22
- https://git.kernel.org/stable/c/a37ef7613c00f2d72c8fc08bd83fb6cc76926c8c
- https://git.kernel.org/stable/c/b7bab33c4623c66e3398d5253870d4e88c52dfc0
- https://git.kernel.org/stable/c/cef0962f2d3e5fd0660c8efb72321083a1b531a9
- https://git.kernel.org/stable/c/deab66596dfad14f1c54eeefdb72428340d72a77
- https://lists.debian.org/debian-lts-announce/2024/06/msg00019.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36960.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36960
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
