# [M] MAGMI plugin for Magento Server Directory Traversal

## Summary
Severity: Medium
Advisory: GHSA-c252-xc8v-mqmm
CVE: CVE-2015-2067
CWE: CWE-22
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-c252-xc8v-mqmm
Type: github-advisory

## Affected
- Packagist: `dweeves/magmi` — affected >=0

## Details
Directory traversal vulnerability in web/ajax_pluginconf.php in the MAGMI (aka Magento Mass Importer) plugin for Magento Server allows remote attackers to read arbitrary files via a .. (dot dot) in the file parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-2067
- https://github.com/dweeves/magmi-git
- https://web.archive.org/web/20210122162452/http://www.securityfocus.com/bid/74881
- http://packetstormsecurity.com/files/130250/Magento-Server-MAGMI-Cross-Site-Scripting-Local-File-Inclusion.html
- http://www.exploit-db.com/exploits/35996
