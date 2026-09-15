# [H] Authenticated FreePBX Music RCE via mpg123 and Asterisk Call Files

## Summary
Severity: High
Advisory: CVE-2026-73662
Aliases: GHSA-p97w-rq48-p8q2
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73662
Type: osv

## Details
FreePBX is an open source IP PBX. From 17.0.1 until 17.0.7, the FreePBX Music on Hold module permits dangerous command-line options for /usr/bin/mpg123 and other allowed players in validateCustomConfiguration() in Music.class.php. An authenticated administrator can use options that write files, open control channels, or create Asterisk call files because applicationUsesDisallowedPlayerOption() does not reject those arguments, resulting in arbitrary command execution as the asterisk service user. This issue is fixed in version 17.0.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73662.json
- https://github.com/FreePBX/security-reporting/security/advisories/GHSA-p97w-rq48-p8q2
- https://nvd.nist.gov/vuln/detail/CVE-2026-73662
- https://github.com/FreePBX/music/commit/9f45605982202a34244ff22c4f635af0dfc1a733
