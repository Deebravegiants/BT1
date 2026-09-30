# [M] Gimp: gimp: double-free in read_layer_block()

## Summary
Severity: Medium
Advisory: CVE-2026-58381
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:H)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-58381
Type: osv

## Details
A flaw was found in GIMP's PSP file format parser. A double-free condition occurs in the read_layer_block() function when processing a specially crafted PSP file. This could allow an attacker to cause memory corruption, potentially leading to denial of service or arbitrary code execution.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2026-58381
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58381.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58381
- https://bugzilla.redhat.com/show_bug.cgi?id=2496166
- https://gitlab.gnome.org/GNOME/gimp/-/issues/16207
- https://gitlab.gnome.org/GNOME/gimp/-/commit/b22e147b
