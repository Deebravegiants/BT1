# [H] Gimp: gimp: multiple vulnerabilities in file format plugins via crafted image file

## Summary
Severity: High
Advisory: CVE-2026-59091
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-59091
Type: osv

## Details
A flaw was found in GIMP's file format plugins, including those for PSD and PAA files. A remote attacker could exploit these vulnerabilities by tricking a user into opening a specially crafted image file. This could lead to unexpected application behavior or other potential security impacts without requiring further user interaction.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://gitlab.gnome.org/GNOME/gimp/-/work_items/16510
- https://access.redhat.com/security/cve/CVE-2026-59091
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59091.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59091
- https://bugzilla.redhat.com/show_bug.cgi?id=2496585
- https://gitlab.gnome.org/GNOME/gimp
