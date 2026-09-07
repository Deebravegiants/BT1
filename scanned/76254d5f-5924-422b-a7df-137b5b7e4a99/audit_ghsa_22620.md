# [M] OpenCart Path Traversal

## Summary
Severity: Medium
Advisory: GHSA-qgrf-34hp-ghm9
CVE: CVE-2018-11495
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-qgrf-34hp-ghm9
Type: github-advisory

## Affected
- Packagist: `opencart/opencart` — affected >=0

## Details
OpenCart through 3.0.2.0 allows directory traversal in the `editDownload` function in `admin\model\catalog\download.php` via `admin/index.php?route=catalog/download/edit`, related to the `download_id`. For example, an attacker can download `../../config.php`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11495
- https://github.com/opencart/opencart
- http://www.bigdiao.cc/2018/05/24/Opencart-v3-0-2-0
