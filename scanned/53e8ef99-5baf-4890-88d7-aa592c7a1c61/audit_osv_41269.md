# [M] Gimp: gimp: denial of service via integer overflow in playstation tim loader

## Summary
Severity: Medium
Advisory: CVE-2026-59089
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-59089
Type: osv

## Details
A flaw was found in GIMP. The PlayStation TIM loader, responsible for handling PlayStation image files, incorrectly calculates the size of the Color Look-Up Table (CLUT) due to an integer overflow. This occurs when multiplying num_colors and num_cluts, both 16-bit unsigned short integers, resulting in a value exceeding the maximum integer limit. An attacker could exploit this by providing a specially crafted image file, leading to undefined behavior and causing the GIMP plug-in to abort, effectively resulting in a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://gitlab.gnome.org/GNOME/gimp/-/work_items/16493
- https://access.redhat.com/security/cve/CVE-2026-59089
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59089.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59089
- https://bugzilla.redhat.com/show_bug.cgi?id=2496583
- https://gitlab.gnome.org/GNOME/gimp
