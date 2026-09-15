# [M] 389-ds-base: null pointer dereference leads to denial of service

## Summary
Severity: Medium
Advisory: CVE-2025-2487
Aliases: GHSA-426r-w669-66gw
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-18
Source: https://osv.dev/vulnerability/CVE-2025-2487
Type: osv

## Details
A flaw was found in the 389-ds-base LDAP Server. This issue occurs when issuing a Modify DN LDAP operation through the ldap protocol, when the function return value is not tested and a NULL pointer is dereferenced. If a privileged user performs a ldap MODDN operation after a failed operation, it could lead to a Denial of Service (DoS) or system crash.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://github.com/389ds/389-ds-base/
- https://access.redhat.com/errata/RHSA-2025:3663
- https://access.redhat.com/errata/RHSA-2025:3670
- https://access.redhat.com/errata/RHSA-2025:4491
- https://access.redhat.com/errata/RHSA-2025:7395
- https://access.redhat.com/security/cve/CVE-2025-2487
- https://github.com/389ds/389-ds-base/security/advisories/GHSA-426r-w669-66gw
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/2xxx/CVE-2025-2487.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-2487
- https://bugzilla.redhat.com/show_bug.cgi?id=2353071
