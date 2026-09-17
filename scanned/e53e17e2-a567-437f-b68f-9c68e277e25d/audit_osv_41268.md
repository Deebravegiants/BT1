# [M] Gimp: gimp: denial of service via signed integer overflow in fli file processing

## Summary
Severity: Medium
Advisory: CVE-2026-59088
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-59088
Type: osv

## Details
A flaw was found in GIMP. A signed integer overflow vulnerability exists in the `file-fli` plugin when processing FLI image files. This occurs due to an incorrect calculation during memory allocation for image buffers, where the multiplication of image width and height can exceed the maximum integer value. A remote attacker could exploit this by tricking a user into opening a specially crafted FLI file, leading to the application crashing and resulting in a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://gitlab.gnome.org/GNOME/gimp/-/work_items/16492
- https://access.redhat.com/security/cve/CVE-2026-59088
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59088.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59088
- https://bugzilla.redhat.com/show_bug.cgi?id=2496582
- https://gitlab.gnome.org/GNOME/gimp
