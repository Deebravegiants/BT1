# [M] Libnbd: libnbd: arbitrary code execution via ssh argument injection through a malicious uri

## Summary
Severity: Medium
Advisory: CVE-2025-14946
CVSS: 4.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2025-12-19
Source: https://osv.dev/vulnerability/CVE-2025-14946
Type: osv

## Details
A flaw was found in libnbd. A malicious actor could exploit this by convincing libnbd to open a specially crafted Uniform Resource Identifier (URI). This vulnerability arises because non-standard hostnames starting with '-o' are incorrectly interpreted as arguments to the Secure Shell (SSH) process, rather than as hostnames. This could lead to arbitrary code execution with the privileges of the user running libnbd.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://libguestfs.org/libnbd-release-notes-1.24.1.html#Security
- https://access.redhat.com/security/cve/CVE-2025-14946
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/14xxx/CVE-2025-14946.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-14946
- https://bugzilla.redhat.com/show_bug.cgi?id=2423789
- https://gitlab.com/nbdkit/libnbd
