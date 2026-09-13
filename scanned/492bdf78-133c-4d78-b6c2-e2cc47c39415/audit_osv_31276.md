# [M] Ovirt-engine: potential exposure of cleartext provider passwords via web ui

## Summary
Severity: Medium
Advisory: CVE-2024-7259
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-09-26
Source: https://osv.dev/vulnerability/CVE-2024-7259
Type: osv

## Details
A flaw was found in oVirt. A user with administrator privileges, including users with the ReadOnlyAdmin permission, may be able to use browser developer tools to view Provider passwords in cleartext.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2024-7259
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/7xxx/CVE-2024-7259.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-7259
- https://bugzilla.redhat.com/show_bug.cgi?id=2314229
- https://github.com/oVirt/ovirt-engine
