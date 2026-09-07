# [H] phpBB has Password Reset Link Poisoning via Host Header injection

## Summary
Severity: High
Advisory: GHSA-7gm6-w7mx-58cr
CVE: CVE-2026-29199
CWE: CWE-640
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-7gm6-w7mx-58cr
Type: github-advisory

## Affected
- Packagist: `phpbb/phpbb` — affected >=3.0.0 <3.3.16
- Packagist: `phpbb/phpbb` — affected >=4.0.0-a1 <4.0.0-a2

## Details
phpBB before 3.3.16 is vulnerable to Host Header Injection that can lead to password rest link poisoning. When force_server_vars is disabled, the servers hostname may be extracted from the HTTP Host header which is used to generate the password reset link URL. An attacker who can manipulate the Host header (e.g. through misconfigured host setup or missing header validation by the webserver) can cause password reset emails to contain a link pointing to an attacker-controlled domain, potentially leading to account takeover.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-29199
- https://hackerone.com/reports/3543246
- https://blog.phpbb.com/2026/04/27/phpbb-4-0-0-a2-release
- https://github.com/phpbb/phpbb-app
- https://www.phpbb.com/community/viewtopic.php?t=2671024
