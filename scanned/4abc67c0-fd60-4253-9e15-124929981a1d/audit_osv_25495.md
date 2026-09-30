# [M] Libvirt: improper locking in virstoragepoolobjlistsearch may lead to denial of service

## Summary
Severity: Medium
Advisory: CVE-2023-3750
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-07-24
Source: https://osv.dev/vulnerability/CVE-2023-3750
Type: osv

## Details
A flaw was found in libvirt. The virStoragePoolObjListSearch function does not return a locked pool as expected, resulting in a race condition and denial of service when attempting to lock the same object from another thread. This issue could allow clients connecting to the read-only socket to crash the libvirt daemon.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EVK6JKP36CHE7YAFDJNPNLTW4OWJJ7TQ/
- https://access.redhat.com/errata/RHSA-2023:6409
- https://access.redhat.com/security/cve/CVE-2023-3750
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3750.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3750
- https://bugzilla.redhat.com/show_bug.cgi?id=2222210
