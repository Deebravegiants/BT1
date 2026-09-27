# [H] Improper account password reset in Craft CMS

## Summary
Severity: High
Advisory: GHSA-5cjr-78cq-3wrg
CVE: CVE-2022-29933
CWE: CWE-640
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-10
Source: https://github.com/advisories/GHSA-5cjr-78cq-3wrg
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=0 <3.7.36

## Details
Craft CMS through 3.7.36 allows a remote unauthenticated attacker, who knows at least one valid username, to reset the account's password and take over the account by providing a crafted HTTP header to the application while using the password reset functionality. Specifically, the attacker must send X-Forwarded-Host to the /index.php?p=admin/actions/users/send-password-reset-email URI. NOTE: the vendor's position is that a customer can already work around this by adjusting the configuration (i.e., by not using the default configuration).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29933
- https://github.com/craftcms/cms
- https://sec-consult.com/vulnerability-lab
- https://sec-consult.com/vulnerability-lab/advisory/password-reset-poisoning-attack-craft-cms
- http://packetstormsecurity.com/files/166989/Craft-CMS-3.7.36-Password-Reset-Poisoning-Attack.html
