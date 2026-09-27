# [M] Capgo - Denial of Service via Improper Password Policy Length Validation

## Summary
Severity: Medium
Advisory: CVE-2026-56228
Aliases: GHSA-vhjp-62qf-33mx
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-20
Source: https://osv.dev/vulnerability/CVE-2026-56228
Type: osv

## Details
Capgo before 12.128.2 fails to enforce a maximum value on the minimum password length field in its password policy configuration. An authenticated organization administrator can set an extremely large numeric value (e.g., billions of characters) as the minimum password length, making compliance impossible for all organization members. Once the policy is enabled, users (including administrators) are unable to change their passwords or access the organization, resulting in an organization-wide account lockout and application-level denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56228.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-vhjp-62qf-33mx
- https://nvd.nist.gov/vuln/detail/CVE-2026-56228
- https://www.vulncheck.com/advisories/capgo-denial-of-service-via-improper-password-policy-length-validation
