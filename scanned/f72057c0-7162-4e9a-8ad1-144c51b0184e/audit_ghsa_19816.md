# [H] com.xwiki.confluencepro:application-confluence-migrator-pro-ui's application homepage is public

## Summary
Severity: High
Advisory: GHSA-3w9f-2pph-j5vc
CVE: CVE-2025-27604
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-07
Source: https://github.com/advisories/GHSA-3w9f-2pph-j5vc
Type: github-advisory

## Affected
- Maven: `com.xwiki.confluencepro:application-confluence-migrator-pro-ui` — affected >=0 <1.11.7

## Details
### Impact
The homepage of the application is public which enables a guest to download the package which might contain sensitive information.

### Patches
1.11.7

### Workarounds
The access to the page can be manually restricted to a specific set of users or groups.

## References
- https://github.com/xwikisas/application-confluence-migrator-pro/security/advisories/GHSA-3w9f-2pph-j5vc
- https://nvd.nist.gov/vuln/detail/CVE-2025-27604
- https://github.com/xwikisas/application-confluence-migrator-pro/commit/6ced42b1f341fd0ce6734fc58c7d694da5f365fb
- https://github.com/xwikisas/application-confluence-migrator-pro
