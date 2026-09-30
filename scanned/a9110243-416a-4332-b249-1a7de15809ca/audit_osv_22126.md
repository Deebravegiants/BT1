# [H] Authenticated remote code execution in octobercms

## Summary
Severity: High
Advisory: CVE-2022-21705
Aliases: GHSA-79jw-2f46-wv22
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-23
Source: https://osv.dev/vulnerability/CVE-2022-21705
Type: osv

## Details
Octobercms is a self-hosted CMS platform based on the Laravel PHP Framework. In affected versions user input was not properly sanitized before rendering. An authenticated user with the permissions to create, modify and delete website pages can exploit this vulnerability to bypass `cms.safe_mode` / `cms.enableSafeMode` in order to execute arbitrary code. This issue only affects admin panels that rely on safe mode and restricted permissions. To exploit this vulnerability, an attacker must first have access to the backend area. The issue has been patched in Build 474 (v1.0.474) and v1.1.10. Users unable to upgrade should apply https://github.com/octobercms/library/commit/c393c5ce9ca2c5acc3ed6c9bb0dab5ffd61965fe to your installation manually.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/21xxx/CVE-2022-21705.json
- https://github.com/octobercms/october/security/advisories/GHSA-79jw-2f46-wv22
- https://nvd.nist.gov/vuln/detail/CVE-2022-21705
- https://github.com/octobercms/library/commit/c393c5ce9ca2c5acc3ed6c9bb0dab5ffd61965fe
