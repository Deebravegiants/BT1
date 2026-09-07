# [M] PHP Server Monitor vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-rq7f-j68f-mqh3
CVE: CVE-2024-5312
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-05-24
Source: https://github.com/advisories/GHSA-rq7f-j68f-mqh3
Type: github-advisory

## Affected
- Packagist: `phpservermon/phpservermon` — affected >=0 <3.3.0

## Details
PHP Server Monitor, version 3.2.0, is vulnerable to an XSS via the /phpservermon-3.2.0/vendor/phpmailer/phpmailer/test_script/index.php page in all visible parameters. An attacker could create a specially crafted URL, send it to a victim and retrieve their session details.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-5312
- https://github.com/PHPMailer/PHPMailer/commit/ff8718f72225a2e34d918c06a3b2c8cca5af3164
- https://github.com/phpservermon/phpservermon
- https://www.incibe.es/en/incibe-cert/notices/aviso/cross-site-scripting-vulnerability-php-server-monitor
