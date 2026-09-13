# [M] 389-ds-base: a heap overflow leading to denail-of-servce while writing a value larger than 256 chars (in log_entry_attr)

## Summary
Severity: Medium
Advisory: CVE-2024-1062
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-12
Source: https://osv.dev/vulnerability/CVE-2024-1062
Type: osv

## Details
A heap overflow flaw was found in 389-ds-base. This issue leads to a denial of service when writing a value larger than 256 chars in log_entry_attr.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://github.com/389ds/389-ds-base/
- https://access.redhat.com/errata/RHSA-2024:1074
- https://access.redhat.com/errata/RHSA-2024:1372
- https://access.redhat.com/errata/RHSA-2024:3047
- https://access.redhat.com/errata/RHSA-2024:4209
- https://access.redhat.com/errata/RHSA-2024:4633
- https://access.redhat.com/errata/RHSA-2024:5690
- https://access.redhat.com/errata/RHSA-2024:7458
- https://access.redhat.com/errata/RHSA-2025:1632
- https://access.redhat.com/security/cve/CVE-2024-1062
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/1xxx/CVE-2024-1062.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-1062
- https://bugzilla.redhat.com/show_bug.cgi?id=2256711
- https://bugzilla.redhat.com/show_bug.cgi?id=2261879
