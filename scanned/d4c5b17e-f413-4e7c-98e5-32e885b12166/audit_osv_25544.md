# [M] Openjpeg: malicious files can cause the program to enter a large loop

## Summary
Severity: Medium
Advisory: CVE-2023-39327
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2024-07-13
Source: https://osv.dev/vulnerability/CVE-2023-39327
Type: osv

## Details
A flaw was found in OpenJPEG. Maliciously constructed pictures can cause the program to enter a large loop and continuously print warning messages on the terminal.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://www.openjpeg.org/
- https://access.redhat.com/errata/RHSA-2026:4128
- https://access.redhat.com/security/cve/CVE-2023-39327
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39327.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-39327
- https://bugzilla.redhat.com/show_bug.cgi?id=2295812
