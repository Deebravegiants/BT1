# [M] Binutils: binutils: denial of service via crafted elf file

## Summary
Severity: Medium
Advisory: CVE-2026-6845
CVSS: 5.0 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-6845
Type: osv

## Details
A flaw was found in binutils, specifically within the `readelf` utility. This vulnerability allows a local attacker to cause a Denial of Service (DoS) by tricking a user into processing a specially crafted Executable and Linkable Format (ELF) file. The exploitation of this flaw can lead to the system becoming unresponsive due to excessive resource consumption or a program crash.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2026:34924
- https://access.redhat.com/errata/RHSA-2026:39022
- https://access.redhat.com/security/cve/CVE-2026-6845
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6845.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-6845
- https://bugzilla.redhat.com/show_bug.cgi?id=2460012
