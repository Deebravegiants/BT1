# [M] Quay: incorrect privilege assignment

## Summary
Severity: Medium
Advisory: CVE-2025-4374
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-05-06
Source: https://osv.dev/vulnerability/CVE-2025-4374
Type: osv

## Details
A flaw was found in Quay. When an organization acts as a proxy cache, and a user or robot pulls an image that hasn't been mirrored yet, they are granted "Admin" permissions on the newly created repository.

## References
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHBA-2025:8262
- https://access.redhat.com/errata/RHBA-2025:8263
- https://access.redhat.com/errata/RHBA-2025:8687
- https://access.redhat.com/errata/RHBA-2025:8688
- https://access.redhat.com/security/cve/CVE-2025-4374
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/4xxx/CVE-2025-4374.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-4374
- https://bugzilla.redhat.com/show_bug.cgi?id=2364267
- https://github.com/quay/quay
