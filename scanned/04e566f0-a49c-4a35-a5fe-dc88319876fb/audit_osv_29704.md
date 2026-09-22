# [C] CVE-2024-45522

## Summary
Severity: Critical
Advisory: CVE-2024-45522
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-09-01
Source: https://osv.dev/vulnerability/CVE-2024-45522
Type: osv

## Details
Linen before cd37c3e does not verify that the domain is linen.dev or www.linen.dev when resetting a password. This occurs in create in apps/web/pages/api/forgot-password/index.ts.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45522.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45522
- https://github.com/Linen-dev/linen.dev/commit/cd37c3e88ec29f4e7baae7e32fe80d0137848d10
