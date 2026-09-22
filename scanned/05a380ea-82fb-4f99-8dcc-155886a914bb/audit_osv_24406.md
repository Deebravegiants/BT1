# [M] Improper authorization check in the server component

## Summary
Severity: Medium
Advisory: CVE-2023-1832
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-10-04
Source: https://osv.dev/vulnerability/CVE-2023-1832
Type: osv

## Details
An improper access control flaw was found in Candlepin. An attacker can create data scoped under another customer/tenant, which can result in loss of confidentiality and availability for the affected customer/tenant.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2023-1832
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1832.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-1832
- https://bugzilla.redhat.com/show_bug.cgi?id=2184364
