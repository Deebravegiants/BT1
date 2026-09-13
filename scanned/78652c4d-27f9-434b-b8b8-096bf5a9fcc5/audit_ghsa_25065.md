# [H] Smarty arbitrary PHP code execution

## Summary
Severity: High
Advisory: GHSA-2pmx-6mm6-6v72
CVE: CVE-2014-8350
CWE: CWE-94
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-2pmx-6mm6-6v72
Type: github-advisory

## Affected
- Packagist: `smarty/smarty` — affected >=0 <3.1.21

## Details
Smarty before 3.1.21 allows remote attackers to bypass the secure mode restrictions and execute arbitrary PHP code as demonstrated by "{literal}<{/literal}script language=php>" in a template.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-8350
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=765920
- https://code.google.com/p/smarty-php/source/browse/trunk/distribution/change_log.txt?r=4902
- https://exchange.xforce.ibmcloud.com/vulnerabilities/97725
- https://github.com/smarty-php/smarty
- http://advisories.mageia.org/MGASA-2014-0468.html
- http://seclists.org/oss-sec/2014/q4/420
- http://seclists.org/oss-sec/2014/q4/421
- http://www.mandriva.com/security/advisories?name=MDVSA-2014:221
- http://www.securityfocus.com/bid/70708
