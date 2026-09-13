# [H] Gimp: integer overflow in file-fits plugin causes a heap-based buffer overflow on crafted fits images

## Summary
Severity: High
Advisory: CVE-2026-66758
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-66758
Type: osv

## Details
A flaw was found in the file-fits plugin in GIMP. When processing a FITS image file, the plugin calculates memory allocation sizes using signed 32-bit integers for width and height. If a crafted file sets both values to large values, their product exceeds 2^31 and overflows, resulting in an undersized heap-based buffer allocation. This integer overflow issue results in a heap-based buffer overflow when cfitsio subsequently writes a full row of pixels in the buffer, causing memory corruption, potentially leading to arbitrary code execution or a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2026:50817
- https://access.redhat.com/errata/RHSA-2026:62507
- https://access.redhat.com/security/cve/CVE-2026-66758
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66758.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-66758
- https://bugzilla.redhat.com/show_bug.cgi?id=2507475
- https://gitlab.gnome.org/GNOME/gimp/-/issues/16528
- https://gitlab.gnome.org/GNOME/gimp
