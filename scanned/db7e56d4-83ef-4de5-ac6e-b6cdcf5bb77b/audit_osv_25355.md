# [M] Imagemagick: heap-buffer-overflow in coders/tiff.c

## Summary
Severity: Medium
Advisory: CVE-2023-3428
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-10-04
Source: https://osv.dev/vulnerability/CVE-2023-3428
Type: osv

## Details
A heap-based buffer overflow vulnerability was found  in coders/tiff.c in ImageMagick. This issue may allow a local attacker to trick the user into opening a specially crafted file, resulting in an application crash and denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2023-3428
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3428.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3428
- https://bugzilla.redhat.com/show_bug.cgi?id=2218369
