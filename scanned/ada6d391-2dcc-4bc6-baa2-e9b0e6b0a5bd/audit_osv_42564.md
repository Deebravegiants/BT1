# [M] Binutils: binutils: denial of service vulnerabilities in readelf via crafted elf files

## Summary
Severity: Medium
Advisory: CVE-2026-6844
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-6844
Type: osv

## Details
A flaw was found in the `readelf` utility of the binutils package. A local attacker could exploit two Denial of Service (DoS) vulnerabilities by providing a specially crafted Executable and Linkable Format (ELF) file. One vulnerability, a resource exhaustion (CWE-400), can lead to an out-of-memory condition. The other, a null pointer dereference (CWE-476), can cause a segmentation fault. Both issues can result in the `readelf` utility becoming unresponsive or crashing, leading to a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2026-6844
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6844.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-6844
- https://bugzilla.redhat.com/show_bug.cgi?id=2460016
