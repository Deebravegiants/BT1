# [C] ThinkPHP Framework vulnerable to remote code execution

## Summary
Severity: Critical
Advisory: GHSA-p4qr-vq2g-22wp
CVE: CVE-2022-47945
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-23
Source: https://github.com/advisories/GHSA-p4qr-vq2g-22wp
Type: github-advisory

## Affected
- Packagist: `topthink/framework` — affected >=0 <6.0.14

## Details
ThinkPHP Framework before 6.0.14 allows local file inclusion via the lang parameter when the language pack feature is enabled (`lang_switch_on=true`). An unauthenticated and remote attacker can exploit this to execute arbitrary operating system commands, as demonstrated by including `pearcmd.php`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-47945
- https://github.com/top-think/framework/commit/c4acb8b4001b98a0078eda25840d33e295a7f099
- https://github.com/top-think/framework
- https://github.com/top-think/framework/compare/v6.0.13...v6.0.14
- https://tttang.com/archive/1865
