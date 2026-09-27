# [H] Gimp: heap buffer overflow in `file-seattle-filmworks` load — `fread` writes attacker-controlled length into undersized allocation

## Summary
Severity: High
Advisory: CVE-2026-59087
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-59087
Type: osv

## Details
A flaw was found in the GIMP image manipulation program, specifically within its Seattle Filmworks file loader. A remote attacker could exploit this vulnerability by tricking a user into opening a specially crafted Seattle Filmworks file. This could lead to a heap overflow, allowing the attacker to write several kilobytes of controlled data beyond the intended memory buffer. Such an overflow can result in memory corruption, potentially leading to arbitrary code execution or a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://gitlab.gnome.org/GNOME/gimp/-/work_items/16491
- https://access.redhat.com/security/cve/CVE-2026-59087
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59087.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59087
- https://bugzilla.redhat.com/show_bug.cgi?id=2496576
- https://gitlab.gnome.org/GNOME/gimp
