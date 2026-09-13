# [H] FreeScout vulnerable to SSRF via Helper::sanitizeRemoteUrl: redirect destination not re-validated, allowing internal HTTP / cloud-metadata access

## Summary
Severity: High
Advisory: CVE-2026-41905
Aliases: GHSA-22wf-848c-c856
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/CVE-2026-41905
Type: osv

## Details
FreeScout is a free help desk and shared inbox built with PHP's Laravel framework. Prior to version 1.8.217, Helper::sanitizeRemoteUrl() in app/Misc/Helper.php follows HTTP redirects via curlGetLastRedirectedUrl() but then re-validates the original URL instead of the final redirect destination. An attacker who can supply any URL that passes the initial host check can redirect FreeScout to internal HTTP services (cloud metadata, internal APIs, RFC1918 ranges) that would normally be blocked. This issue has been patched in version 1.8.217.

## References
- https://github.com/freescout-help-desk/freescout/releases/tag/1.8.217
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41905.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-22wf-848c-c856
- https://nvd.nist.gov/vuln/detail/CVE-2026-41905
