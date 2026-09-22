# [M] Uncontrolled recursion in the Ion reader in Amazon Ion-C before 1.1.6

## Summary
Severity: Medium
Advisory: CVE-2026-84851
Aliases: GHSA-9gfg-hgj4-gh44
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-84851
Type: osv

## Details
An uncontrolled recursion issue exists in Amazon Ion-C versions before 1.1.6 that might allow a remote unauthenticated actor to craft Ion data that exhausts the native call stack and crashes the application using the library, resulting in a denial of service.

## References
- https://aws.amazon.com/security/security-bulletins/2026-094-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84851.json
- https://github.com/amazon-ion/ion-c/security/advisories/GHSA-9gfg-hgj4-gh44
- https://nvd.nist.gov/vuln/detail/CVE-2026-84851
- https://github.com/amazon-ion/ion-c/releases/tag/v1.1.6
