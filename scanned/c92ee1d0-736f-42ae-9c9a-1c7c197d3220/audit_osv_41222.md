# [H] Gimp: gimp: integer overflow in read_rle_channel()

## Summary
Severity: High
Advisory: CVE-2026-58384
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-58384
Type: osv

## Details
A flaw was found in GIMP's PSD parser. An integer overflow in read_RLE_channel() can cause an undersized heap allocation for the RLE row-length table, after which subsequent per-row writes corrupt heap memory. This could lead to memory corruption, potentially resulting in denial of service or arbitrary code execution.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2026:40751
- https://access.redhat.com/security/cve/CVE-2026-58384
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58384.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58384
- https://bugzilla.redhat.com/show_bug.cgi?id=2497431
- https://gitlab.gnome.org/GNOME/gimp/-/issues/16216
- https://gitlab.gnome.org/GNOME/gimp/-/commit/da29e217
