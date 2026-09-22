# [M] Shopware XXE Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6m27-7cqj-2mxw
CVE: CVE-2017-18357
CWE: CWE-610
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-6m27-7cqj-2mxw
Type: github-advisory

## Affected
- Packagist: `shopware/shopware` — affected >=0 <5.3.4

## Details
Shopware before 5.3.4 has a PHP Object Instantiation issue via the sort parameter to the loadPreviewAction() method of the Shopware_Controllers_Backend_ProductStream controller, with resultant XXE via instantiation of a SimpleXMLElement object.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18357
- https://blog.ripstech.com/2017/shopware-php-object-instantiation-to-blind-xxe
- https://demo.ripstech.com/projects/shopware_5.3.3
- http://packetstormsecurity.com/files/152995/Shopware-createInstanceFromNamedArguments-PHP-Object-Instantiation.html
