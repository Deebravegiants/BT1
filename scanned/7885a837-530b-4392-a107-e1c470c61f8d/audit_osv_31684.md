# [H] tgstation-server's role authorization incorrectly OR'd with user's enabled status

## Summary
Severity: High
Advisory: CVE-2025-21611
Aliases: GHSA-rf5r-q276-vrc4
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-06
Source: https://osv.dev/vulnerability/CVE-2025-21611
Type: osv

## Details
tgstation-server is a production scale tool for BYOND server management. Prior to 6.12.3, roles used to authorize API methods were incorrectly OR'd instead of AND'ed with the role used to determine if a user was enabled. This allows enabled users access to most, but not all, authorized actions regardless of their permissions. Notably, the WriteUsers right is unaffected so users may not use this bug to permanently elevate their account permissions. The fix is release in tgstation-server-v6.12.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21611.json
- https://github.com/tgstation/tgstation-server/security/advisories/GHSA-rf5r-q276-vrc4
- https://nvd.nist.gov/vuln/detail/CVE-2025-21611
- https://github.com/tgstation/tgstation-server/issues/2064
- https://github.com/tgstation/tgstation-server/commit/e7b1189620baaf03c2d23f6e164d07c7c7d87d57
