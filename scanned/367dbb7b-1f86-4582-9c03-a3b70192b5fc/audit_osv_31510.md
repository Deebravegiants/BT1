# [M] Libvirt: information disclosure via world-readable vm snapshots

## Summary
Severity: Medium
Advisory: CVE-2025-13193
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-11-17
Source: https://osv.dev/vulnerability/CVE-2025-13193
Type: osv

## Details
A flaw was found in libvirt. External inactive snapshots for shut-down VMs are incorrectly created as world-readable, making it possible for unprivileged users to inspect the guest OS contents. This results in an information disclosure vulnerability.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2025-13193
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/13xxx/CVE-2025-13193.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-13193
- https://bugzilla.redhat.com/show_bug.cgi?id=2415409
- https://gitlab.com/libvirt/libvirt
