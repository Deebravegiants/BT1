# [H] Laravel Framework RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-qvqm-h22r-4cp9
CVE: CVE-2018-15133
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-qvqm-h22r-4cp9
Type: github-advisory

## Affected
- Packagist: `laravel/framework` — affected >=0
- Packagist: `laravel/framework` — affected >=5.6.0 <5.6.30

## Details
In Laravel Framework through 5.5.40 and 5.6.x through 5.6.29, remote code execution might occur as a result of an unserialize call on a potentially untrusted X-XSRF-TOKEN value. This involves the decrypt method in `Illuminate/Encryption/Encrypter.php` and PendingBroadcast in `gadgetchains/Laravel/RCE/3/chain.php` in phpggc. The attacker must know the application key, which normally would never occur, but could happen if the attacker previously had privileged access or successfully accomplished a previous attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-15133
- https://github.com/laravel/framework/commit/d84cf988ed5d4661a4bf1fdcb08f5073835083a0
- https://github.com/kozmic/laravel-poc-CVE-2018-15133
- https://github.com/laravel/framework
- https://laravel.com/docs/5.6/upgrade#upgrade-5.6.30
- http://packetstormsecurity.com/files/153641/PHP-Laravel-Framework-Token-Unserialize-Remote-Command-Execution.html
