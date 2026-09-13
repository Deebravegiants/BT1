# [H] vfio/pci: Check BAR resources before exporting a DMABUF

## Summary
Severity: High
Advisory: CVE-2026-64042
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64042
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

vfio/pci: Check BAR resources before exporting a DMABUF

A DMABUF exports access to BAR resources and, although they are
requested at startup time, we need to ensure they really were reserved
before exporting.  Otherwise, it's possible to access unreserved
resources through the export.

Add a check to the DMABUF-creation path.

## References
- https://git.kernel.org/stable/c/702809dabdecca807bdd50cfdcc1c980feb2ba62
- https://git.kernel.org/stable/c/8443cd4497a4498c4b01058d76a92116244cb605
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64042.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64042
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
