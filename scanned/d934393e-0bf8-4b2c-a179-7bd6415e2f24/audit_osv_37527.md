# [M] JumpServer Improper Certificate Validation in Custom SMS API Client

## Summary
Severity: Medium
Advisory: CVE-2026-31798
Aliases: GHSA-26pj-mmxw-w3w7
CVSS: 5.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-31798
Type: osv

## Details
JumpServer is an open source bastion host and an operation and maintenance security audit system. Prior to v4.10.16-lts, JumpServer improperly validates certificates in the Custom SMS API Client. When JumpServer sends MFA/OTP codes via Custom SMS API, an attacker can intercept the request and capture the verification code BEFORE it reaches the user's phone. This vulnerability is fixed in v4.10.16-lts.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31798.json
- https://github.com/jumpserver/jumpserver/security/advisories/GHSA-26pj-mmxw-w3w7
- https://nvd.nist.gov/vuln/detail/CVE-2026-31798
