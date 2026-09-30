# [M] Libvirt: crash of virtinterfaced via virconnectlistinterfaces()

## Summary
Severity: Medium
Advisory: CVE-2024-8235
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-08-30
Source: https://osv.dev/vulnerability/CVE-2024-8235
Type: osv

## Details
A flaw was found in libvirt. A refactor of the code fetching the list of interfaces for multiple APIs introduced a corner case on platforms where allocating 0 bytes of memory results in a NULL pointer. This corner case would lead to a NULL-pointer dereference and subsequent crash of virtinterfaced. This issue could allow clients connecting to the read-only socket to crash the virtinterfaced daemon.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.libvirt.org/archives/list/devel@lists.libvirt.org/thread/X6WOVCL6QF3FQRFIIXL736RFZVSUWLWJ/
- https://access.redhat.com/errata/RHSA-2024:9128
- https://access.redhat.com/security/cve/CVE-2024-8235
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/8xxx/CVE-2024-8235.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-8235
- https://security.netapp.com/advisory/ntap-20240920-0006/
- https://bugzilla.redhat.com/show_bug.cgi?id=2308680
- https://gitlab.com/libvirt/libvirt
