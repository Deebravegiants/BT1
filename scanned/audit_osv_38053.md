# [M] Binutils: gnu binutils: information disclosure or denial of service via out-of-bounds read in bfd linker

## Summary
Severity: Medium
Advisory: CVE-2026-3442
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:L)
Published: 2026-03-15
Source: https://osv.dev/vulnerability/CVE-2026-3442
Type: osv

## Details
A flaw was found in GNU Binutils. This vulnerability, a heap-based buffer overflow, specifically an out-of-bounds read, exists in the bfd linker component. An attacker could exploit this by convincing a user to process a specially crafted malicious XCOFF object file. Successful exploitation may lead to the disclosure of sensitive information or cause the application to crash, resulting in an application level denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2026:33527
- https://access.redhat.com/errata/RHSA-2026:39022
- https://access.redhat.com/security/cve/CVE-2026-3442
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3442.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-3442
- https://bugzilla.redhat.com/show_bug.cgi?id=2443828
