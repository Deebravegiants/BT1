# [M] Gimp: signed integer overflow in file-sgi (sgi-lib) causes the plugin to crash on rle sgi images

## Summary
Severity: Medium
Advisory: CVE-2026-66757
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-66757
Type: osv

## Details
A flaw was found in the file-sgi plugin in GIMP. When processing an RLE-compressed SGI image, the plugin allocates memory for a row table. The image header dimensions (ysize and zsize) are read as 16-bit unsigned integers. If a crafted file sets both dimensions to their maximum value (65535), the multiplication ysize * zsize overflows the standard 32-bit int boundary before being passed to calloc. This integer overflow issue results in undefined behavior, aborting the plugin and causing a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://gitlab.gnome.org/GNOME/gimp/-/work_items/16494
- https://access.redhat.com/security/cve/CVE-2026-66757
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66757.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-66757
- https://bugzilla.redhat.com/show_bug.cgi?id=2507465
- https://gitlab.gnome.org/GNOME/gimp
