# [H] nophp vulnerable to shell command injection on httpd user when sending a password-setting mail or mail-login mail

## Summary
Severity: High
Advisory: CVE-2023-28854
Aliases: GHSA-9858-q3c2-9wwm
CVSS: 8.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-04-03
Source: https://osv.dev/vulnerability/CVE-2023-28854
Type: osv

## Details
nophp is a PHP web framework. Prior to version 0.0.1, nophp is vulnerable to shell command injection on httpd user. A patch was made available at commit e5409aa2d441789cbb35f6b119bef97ecc3986aa on 2023-03-30. Users should update index.php to 2023-03-30 or later or, as a workaround, add a function such as `env_patchsample230330.php` to env.php.

## References
- https://github.com/paijp/nophp/releases/tag/v0.0.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28854.json
- https://github.com/paijp/nophp/security/advisories/GHSA-9858-q3c2-9wwm
- https://nvd.nist.gov/vuln/detail/CVE-2023-28854
- https://github.com/paijp/nophp/commit/e5409aa2d441789cbb35f6b119bef97ecc3986aa
