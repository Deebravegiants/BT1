# [H] Poppler: pdfinfo: crash in broken documents when using -dests parameter

## Summary
Severity: High
Advisory: CVE-2024-6239
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-21
Source: https://osv.dev/vulnerability/CVE-2024-6239
Type: osv

## Details
A flaw was found in the Poppler's Pdfinfo utility. This issue occurs when using -dests parameter with pdfinfo utility. By using certain malformed input files, an attacker could cause the utility to crash, leading to a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2024:5305
- https://access.redhat.com/errata/RHSA-2024:9167
- https://access.redhat.com/security/cve/CVE-2024-6239
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6239.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6239
- https://bugzilla.redhat.com/show_bug.cgi?id=2293594
- https://gitlab.freedesktop.org/poppler/poppler
