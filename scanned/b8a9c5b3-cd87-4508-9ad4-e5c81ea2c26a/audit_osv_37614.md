# [H] ZITADEL: Reactivation of Expired Passkey Registration Codes

## Summary
Severity: High
Advisory: CVE-2026-32132
Aliases: GHSA-2x66-r53r-9r86
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-32132
Type: osv

## Details
ZITADEL is an open source identity management platform. Prior to 3.4.8 and 4.12.2, a potential vulnerability exists in Zitadel's passkey registration endpoints. This endpoint allows registering a new passkey using a previously retrieved code. An improper expiration check of the code, could allow an attacker to potentially register their own passkey and gain access to the victim's account. This vulnerability is fixed in 3.4.8 and 4.12.2.

## References
- https://github.com/zitadel/zitadel/releases/tag/v3.4.8
- https://github.com/zitadel/zitadel/releases/tag/v4.12.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32132.json
- https://github.com/zitadel/zitadel/security/advisories/GHSA-2x66-r53r-9r86
- https://nvd.nist.gov/vuln/detail/CVE-2026-32132
