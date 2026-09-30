# [M] Luksmeta: data corruption when handling luks1 partitions with luksmeta

## Summary
Severity: Medium
Advisory: CVE-2025-11568
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-10-15
Source: https://osv.dev/vulnerability/CVE-2025-11568
Type: osv

## Details
A data corruption vulnerability has been identified in the luksmeta utility when used with the LUKS1 disk encryption format. An attacker with the necessary permissions can exploit this flaw by writing a large amount of metadata to an encrypted device. The utility fails to correctly validate the available space, causing the metadata to overwrite and corrupt the user's encrypted data. This action leads to a permanent loss of the stored information. Devices using the LUKS formats other than LUKS1 are not affected by this issue.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2025:23086
- https://access.redhat.com/errata/RHSA-2026:18421
- https://access.redhat.com/errata/RHSA-2026:18824
- https://access.redhat.com/security/cve/CVE-2025-11568
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/11xxx/CVE-2025-11568.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-11568
- https://bugzilla.redhat.com/show_bug.cgi?id=2404244
- https://github.com/latchset/luksmeta/pull/16
- https://github.com/latchset/luksmeta
