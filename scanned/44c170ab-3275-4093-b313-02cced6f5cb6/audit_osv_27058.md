# [H] Ovirt: authentication bypass

## Summary
Severity: High
Advisory: CVE-2024-0822
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-01-25
Source: https://osv.dev/vulnerability/CVE-2024-0822
Type: osv

## Details
An authentication bypass vulnerability was found in overt-engine. This flaw allows the creation of users in the system without authentication due to a flaw in the CreateUserSession command.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://ovirt.org/
- https://access.redhat.com/errata/RHSA-2024:0934
- https://access.redhat.com/security/cve/CVE-2024-0822
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0822.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0822
- https://bugzilla.redhat.com/show_bug.cgi?id=2258509
- https://github.com/oVirt/ovirt-engine/pull/914
