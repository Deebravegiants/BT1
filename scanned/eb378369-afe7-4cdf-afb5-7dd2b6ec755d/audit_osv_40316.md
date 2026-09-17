# [H] drm/xe/dma-buf: fix UAF with retry loop

## Summary
Severity: High
Advisory: CVE-2026-52950
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52950
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/dma-buf: fix UAF with retry loop

Retry doesn't work here, since bo will be freed on error, leading to
UAF. However, now that we do the alloc & init before the attach, we can
now combine this as one unit and have the init do the alloc for us. This
should make the retry safe.

Reported by Sashiko.

v2: Fix up the error unwind (CI)

(cherry picked from commit 479669418253e0f27f8cf5db01a731352ea592e7)

## References
- https://git.kernel.org/stable/c/155a372a1cc50fa93387c5d3cdfd614a61e1afd1
- https://git.kernel.org/stable/c/39fdac6be02eb7c3460518c1c4085f75f935c4ce
- https://git.kernel.org/stable/c/827062952ed9bdf4220466c1f05ce452d04bdedf
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-52950.json
- https://access.redhat.com/errata/RHSA-2026:42919
- https://access.redhat.com/errata/RHSA-2026:45192
- https://access.redhat.com/security/cve/CVE-2026-52950
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52950.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52950
- https://bugzilla.redhat.com/show_bug.cgi?id=2492318
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
