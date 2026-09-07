# [M] Craft CMS stores arbitrary content provided by unauthenticated users in session files

## Summary
Severity: Medium
Advisory: GHSA-7vrx-9684-xrf2
CVE: CVE-2025-35939
CWE: CWE-472
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N/E:H (CVSS_V3)
Published: 2025-05-08
Source: https://github.com/advisories/GHSA-7vrx-9684-xrf2
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-alpha.1 <5.7.5
- Packagist: `craftcms/cms` — affected >=0 <4.15.3

## Details
Craft CMS stores arbitrary content provided by unauthenticated users in session files. This content could be accessed and executed, possibly using an independent vulnerability. Craft CMS redirects requests that require authentication to the login page and generates a session file on the server at `/var/lib/php/sessions`. Such session files are named `sess_[session_value]`, where `[session_value]` is provided to the client in a `Set-Cookie` response header. Craft CMS stores the return URL requested by the client without sanitizing parameters. Consequently, an unauthenticated client can introduce arbitrary values, such as PHP code, to a known local file location on the server. Craft CMS versions 5.7.5 and 4.15.3 have been released to address this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-35939
- https://github.com/craftcms/cms/pull/17220
- https://github.com/craftcms/cms/commit/e4c7bac8f31010aee048409f9ef6f744a83146b2
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/4.15.3
- https://github.com/craftcms/cms/releases/tag/5.7.5
- https://raw.githubusercontent.com/cisagov/CSAF/develop/csaf_files/IT/white/2025/va-25-147-01.json
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-35939
- https://www.cve.org/CVERecord?id=CVE-2025-35939
