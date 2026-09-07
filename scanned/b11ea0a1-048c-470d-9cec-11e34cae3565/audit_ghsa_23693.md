# [M] XSS in baserCMS before 4.1.4

## Summary
Severity: Medium
Advisory: GHSA-fx2m-5m9v-jhgp
CVE: CVE-2018-18943
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-fx2m-5m9v-jhgp
Type: github-advisory

## Affected
- Packagist: `baserproject/basercms` — affected >=0 <4.1.4

## Details
An issue was discovered in baserCMS before 4.1.4. In the Register New Category feature of the Upload menu, the category name can be used for XSS via the `data[UploaderCategory][name]` parameter to an `admin/uploader/uploader_categories/edit` URI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-18943
- https://web.archive.org/web/20200130073341/https://basercms.net/release/4_1_4
- https://web.archive.org/web/20211209034642/http://sunu11.com/2018/10/31/baserCMS
