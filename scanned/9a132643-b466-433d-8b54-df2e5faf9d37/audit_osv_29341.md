# [H] CVE-2024-42010

## Summary
Severity: High
Advisory: CVE-2024-42010
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-08-05
Source: https://osv.dev/vulnerability/CVE-2024-42010
Type: osv

## Details
mod_css_styles in Roundcube through 1.5.7 and 1.6.x through 1.6.7 insufficiently filters Cascading Style Sheets (CSS) token sequences in rendered e-mail messages, allowing a remote attacker to obtain sensitive information.

## References
- https://github.com/roundcube/roundcubemail/releases/tag/1.5.8
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.8
- https://roundcube.net/news/2024/08/04/security-updates-1.6.8-and-1.5.8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42010.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42010
- https://github.com/roundcube/roundcubemail/releases
- https://sonarsource.com/blog/government-emails-at-risk-critical-cross-site-scripting-vulnerability-in-roundcube-webmail/
