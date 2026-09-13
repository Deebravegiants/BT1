# [M] 389-ds-base: unauthenticated user can trigger a dos by sending a specific extended search request

## Summary
Severity: Medium
Advisory: CVE-2024-6237
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-07-09
Source: https://osv.dev/vulnerability/CVE-2024-6237
Type: osv

## Details
A flaw was found in the 389 Directory Server. This flaw allows an unauthenticated user to cause a systematic server crash while sending a specific extended search request, leading to a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2024:4997
- https://access.redhat.com/errata/RHSA-2024:5192
- https://access.redhat.com/security/cve/CVE-2024-6237
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6237.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6237
- https://bugzilla.redhat.com/show_bug.cgi?id=2293579
- https://github.com/389ds/389-ds-base/issues/5989
- https://github.com/389ds/389-ds-base
