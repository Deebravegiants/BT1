# [M] CVAT vulnerable to email verification bypass by use of basic authentication

## Summary
Severity: Medium
Advisory: CVE-2025-54573
Aliases: GHSA-fxgh-m76j-242q
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-07-30
Source: https://osv.dev/vulnerability/CVE-2025-54573
Type: osv

## Details
CVAT is an open source interactive video and image annotation tool for computer vision. In versions 1.1.0 through 2.41.0, email verification was not enforced when using Basic HTTP Authentication. As a result, users could create accounts using fake email addresses and use the product as verified users. Additionally, the missing email verification check leaves the system open to bot signups and further usage. CVAT 2.42.0 and later versions contain a fix for the issue. CVAT Enterprise customers have a workaround available; those customers may disable registration to prevent this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54573.json
- https://github.com/cvat-ai/cvat/security/advisories/GHSA-fxgh-m76j-242q
- https://nvd.nist.gov/vuln/detail/CVE-2025-54573
- https://github.com/cvat-ai/cvat/commit/bc20eff16b8406fbb755f6540e6f269da0c9c5b2
