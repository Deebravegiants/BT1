# [M] phpMyAdmin vulnerable to XML external entity (XXE) injection attack

## Summary
Severity: Medium
Advisory: GHSA-q4mm-89q2-xffg
CVE: CVE-2011-4107
CWE: CWE-200, CWE-611
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-q4mm-89q2-xffg
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=3.4.0 <3.4.7.1
- Packagist: `phpmyadmin/phpmyadmin` — affected >=3.3.0 <3.3.10.5

## Details
The `simplexml_load_string` function in the XML import plug-in (`libraries/import/xml.php`) in phpMyAdmin 3.4.x before 3.4.7.1 and 3.3.x before 3.3.10.5 allows remote authenticated users to read arbitrary files via XML data containing external entity references, aka an XML external entity (XXE) injection attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4107
- https://github.com/phpmyadmin/phpmyadmin/commit/2fbf631384fd8cded55f4500cb87b129442f9ed2
- https://github.com/phpmyadmin/phpmyadmin/commit/34d99de000de9d15cfdf5e9cc8b7682d51110bbd
- https://github.com/phpmyadmin/phpmyadmin/commit/5fa86b8e81565c15ddbc359e8f59ecd829a2b717
- https://github.com/phpmyadmin/phpmyadmin/commit/a5e206fbd2ca814042cfc1bb7dd3b40c28ce3fb5
- https://bugzilla.redhat.com/show_bug.cgi?id=751112
- https://exchange.xforce.ibmcloud.com/vulnerabilities/71108
- https://github.com/phpmyadmin/phpmyadmin
- http://lists.fedoraproject.org/pipermail/package-announce/2011-November/069625.html
- http://lists.fedoraproject.org/pipermail/package-announce/2011-November/069635.html
- http://lists.fedoraproject.org/pipermail/package-announce/2011-November/069649.html
- http://packetstormsecurity.org/files/view/106511/phpmyadmin-fileread.txt
- http://seclists.org/fulldisclosure/2011/Nov/21
- http://securityreason.com/securityalert/8533
- http://www.debian.org/security/2012/dsa-2391
- http://www.openwall.com/lists/oss-security/2011/11/03/3
- http://www.openwall.com/lists/oss-security/2011/11/03/5
- http://www.phpmyadmin.net/home_page/security/PMASA-2011-17.php
