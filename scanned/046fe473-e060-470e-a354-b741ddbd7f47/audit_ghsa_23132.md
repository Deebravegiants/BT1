# [M] ImpressCMS Path Traversal to Arbitrary File Delete

## Summary
Severity: Medium
Advisory: GHSA-wcj4-ff9m-5r7g
CVE: CVE-2014-1836
CWE: CWE-22
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-wcj4-ff9m-5r7g
Type: github-advisory

## Affected
- Packagist: `impresscms/impresscms` — affected >=0 <1.3.6

## Details
Absolute path traversal vulnerability in `htdocs/libraries/image-editor/image-edit.php` in ImpressCMS before 1.3.6 allows remote attackers to delete arbitrary files via a full pathname in the `image_path` parameter in a cancel action.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-1836
- https://github.com/ImpressCMS/impresscms/issues/914
- https://github.com/pedrib/PoC/blob/master/generic/impresscms-1.3.5.txt
- https://web.archive.org/web/20200228234251/http://www.securityfocus.com/bid/65279
- http://community.impresscms.org/modules/smartsection/item.php?itemid=675
- http://seclists.org/fulldisclosure/2014/Feb/14
