# [H] Gimp: integer overflow in pcx loader (planes=4) leads to heap overflow on 32-bit

## Summary
Severity: High
Advisory: CVE-2026-78465
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-78465
Type: osv

## Details
A flaw was found in the file-pcx plugin in GIMP, affecting 32-bit builds only. When processing a PCX image file, the plugin calculates memory allocation sizes based on the image dimensions and the number of color planes. If a crafted file sets the number of planes to 4 alongside sufficiently large dimensions, the calculation exceeds the 32-bit integer limit and overflows, resulting in an undersized heap-based buffer allocation. This integer overflow issue results in a heap-based buffer overflow when the plugin subsequently writes image data into the undersized buffer, causing memory corruption, potentially leading to arbitrary code execution or a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://gitlab.gnome.org/GNOME/gimp/-/work_items/16578
- https://access.redhat.com/security/cve/CVE-2026-78465
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78465.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-78465
- https://bugzilla.redhat.com/show_bug.cgi?id=2522057
- https://gitlab.gnome.org/GNOME/gimp
