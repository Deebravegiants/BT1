# [M] Moodle vulnerable to Cross-site scripting

## Summary
Severity: Medium
Advisory: GHSA-v759-3wr5-p294
CVE: CVE-2008-1502
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-v759-3wr5-p294
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <1.8.5

## Details
The `_bad_protocol_once` function in `phpgwapi/inc/class.kses.inc.php` in KSES, as used in eGroupWare before 1.4.003, Moodle before 1.8.5, and other products, allows remote attackers to bypass HTML filtering and conduct cross-site scripting (XSS) attacks via a string containing crafted URL protocols.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-1502
- https://exchange.xforce.ibmcloud.com/vulnerabilities/41435
- https://github.com/moodle/moodle
- https://usn.ubuntu.com/658-1
- https://web.archive.org/web/20080709031015/http://www.securityfocus.com/bid/28424
- https://web.archive.org/web/20080828131802/http://secunia.com/advisories/31017
- https://web.archive.org/web/20080905011948/http://secunia.com/advisories/31018
- https://web.archive.org/web/20081011001554/http://secunia.com/advisories/31167
- https://web.archive.org/web/20081025081058/http://secunia.com/advisories/32400
- https://web.archive.org/web/20081028073531/http://secunia.com/advisories/32446
- https://web.archive.org/web/20090129193143/http://secunia.com/advisories/30986
- https://web.archive.org/web/20100819022833/http://secunia.com/advisories/30073
- https://web.archive.org/web/20120719035305/http://secunia.com/advisories/29491
- https://www.redhat.com/archives/fedora-package-announce/2008-July/msg00331.html
- http://docs.moodle.org/en/Release_Notes#Moodle_1.8.5
- http://lists.opensuse.org/opensuse-security-announce/2008-07/msg00006.html
- http://www.debian.org/security/2008/dsa-1691
- http://www.debian.org/security/2009/dsa-1871
- http://www.egroupware.org/changelog
- http://www.egroupware.org/viewvc/branches/1.4/phpgwapi/inc/class.kses.inc.php?r1=23625&r2=25110&pathrev=25110
