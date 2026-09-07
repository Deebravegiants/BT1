# [H] RCE in baserCMS before 4.1.4

## Summary
Severity: High
Advisory: GHSA-rjc2-x53r-6c9r
CVE: CVE-2018-18942
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-rjc2-x53r-6c9r
Type: github-advisory

## Affected
- Packagist: `baserproject/basercms` — affected >=0 <4.1.4

## Details
In baserCMS before 4.1.4, `lib\Baser\Model\ThemeConfig.php` allows remote attackers to execute arbitrary PHP code via the `admin/theme_configs/form data[ThemeConfig][logo]` parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-18942
- https://github.com/baserproject/basercms/issues/959
- https://web.archive.org/web/20200130073341/https://basercms.net/release/4_1_4
- https://web.archive.org/web/20211209034642/http://sunu11.com/2018/10/31/baserCMS
