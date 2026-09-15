# [H] Nextcloud: Authentication Bypass in ID4me handling via Missing JWT Signature Verification in User OIDC

## Summary
Severity: High
Advisory: CVE-2026-45156
Aliases: GHSA-qqgv-fqwp-mjpp
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-45156
Type: osv

## Details
Nextcloud is an open source content collaboration platform. From versions 0.3.0 to before 3.1.0, 5.0.0 to before 5.1.0, and 6.0.0 to before 6.4.0, a missing signature verification in User OIDC allowed a malicious ID4me authority to identify as any user. This issue has been patched in versions 3.1.0, 4.1.0, 5.1.0, 6.4.0 and 8.3.0.

## References
- https://hackerone.com/reports/3489490
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45156.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-qqgv-fqwp-mjpp
- https://nvd.nist.gov/vuln/detail/CVE-2026-45156
- https://github.com/nextcloud/user_oidc/pull/1285
