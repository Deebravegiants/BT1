# [H] Binutils: binutils: arbitrary code execution via malformed xcoff object file processing

## Summary
Severity: High
Advisory: CVE-2026-6846
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-6846
Type: osv

## Details
A flaw was found in binutils. A heap-buffer-overflow vulnerability exists when processing a specially crafted XCOFF (Extended Common Object File Format) object file during linking. A local attacker could trick a user into processing this malicious file, which could lead to arbitrary code execution, allowing the attacker to run unauthorized commands, or cause a denial of service, making the system unavailable.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-6846.json
- https://access.redhat.com/errata/RHSA-2026:33527
- https://access.redhat.com/errata/RHSA-2026:39022
- https://access.redhat.com/security/cve/CVE-2026-6846
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6846.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-6846
- https://bugzilla.redhat.com/show_bug.cgi?id=2460006
- https://sourceware.org/git/binutils-gdb.git
