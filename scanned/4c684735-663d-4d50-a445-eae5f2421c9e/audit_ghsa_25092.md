# [M] MAGMI cross-site scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-27v2-398x-f74x
CVE: CVE-2015-2068
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-27v2-398x-f74x
Type: github-advisory

## Affected
- Packagist: `dweeves/magmi` — affected >=0 <0.7.22

## Details
Multiple cross-site scripting (XSS) vulnerabilities in the MAGMI (aka Magento Mass Importer) plugin for Magento Server allow remote attackers to inject arbitrary web script or HTML via the (1) profile parameter to web/magmi.php or (2) QUERY_STRING to web/magmi_import_run.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-2068
- https://github.com/dweeves/magmi-git
- http://packetstormsecurity.com/files/130250/Magento-Server-MAGMI-Cross-Site-Scripting-Local-File-Inclusion.html
- http://www.exploit-db.com/exploits/35996
- http://www.securityfocus.com/bid/74879
