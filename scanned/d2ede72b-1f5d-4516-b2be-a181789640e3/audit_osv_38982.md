# [H] vhost: move vdpa group bound check to vhost_vdpa

## Summary
Severity: High
Advisory: CVE-2026-43248
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43248
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

vhost: move vdpa group bound check to vhost_vdpa

Remove duplication by consolidating these here.  This reduces the
posibility of a parent driver missing them.

While we're at it, fix a bug in vdpa_sim where a valid ASID can be
assigned to a group equal to ngroups, causing an out of bound write.

## References
- https://git.kernel.org/stable/c/406db68f9cb976a8ddfafd631197264f2307e9c9
- https://git.kernel.org/stable/c/7441d35d14d9a3d66d925d90cb73c75394e6d454
- https://git.kernel.org/stable/c/cd025c1e876b4e262e71398236a1550486a73ede
- https://git.kernel.org/stable/c/ddb57354634b6ba851b79da45f1de42c646f27d0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43248.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43248
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
