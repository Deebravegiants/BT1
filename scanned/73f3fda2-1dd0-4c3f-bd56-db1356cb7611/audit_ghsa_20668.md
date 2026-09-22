# [H] exceedone/exment and exceedone/laravel-admin SQL Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-p74q-2pf8-j5jx
CVE: CVE-2022-37333
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-25
Source: https://github.com/advisories/GHSA-p74q-2pf8-j5jx
Type: github-advisory

## Affected
- Packagist: `exceedone/exment` — affected >=5.0.0 <5.0.3
- Packagist: `exceedone/exment` — affected >=0 <4.4.3
- Packagist: `exceedone/laravel-admin` — affected >=0 <2.2.3
- Packagist: `exceedone/laravel-admin` — affected >=3.0.0 <3.0.1

## Details
SQL injection vulnerability in the Exment ((PHP8) exceedone/exment v5.0.2 and earlier and exceedone/laravel-admin v3.0.0 and earlier, (PHP7) exceedone/exment v4.4.2 and earlier and exceedone/laravel-admin v2.2.2 and earlier) allows remote authenticated attackers to execute arbitrary SQL commands.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-37333
- https://exment.net/docs/#/release_note?id=v503-20220817
- https://exment.net/docs/#/weakness/20220817
- https://github.com/exceedone/exment
- https://jvn.jp/en/jp/JVN46239102/index.html
