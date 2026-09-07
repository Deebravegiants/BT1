# [M] Improper Restriction of XML External Entity Reference in Castor

## Summary
Severity: Medium
Advisory: GHSA-jwwr-fjgh-cv2x
CVE: CVE-2014-3004
CWE: CWE-611
Ecosystem: Maven
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-jwwr-fjgh-cv2x
Type: github-advisory

## Affected
- Maven: `org.codehaus.castor:castor` — affected >=0 <1.3.3
- Maven: `castor:castor` — affected >=0

## Details
The default configuration for the Xerces SAX Parser in Castor before 1.3.3 allows context-dependent attackers to conduct XML External Entity (XXE) attacks via a crafted XML document.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3004
- https://github.com/castor-data-binding/castor
- https://quickview.cloudapps.cisco.com/quickview/bug/CSCvm56811
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- http://lists.opensuse.org/opensuse-updates/2014-06/msg00043.html
- http://packetstormsecurity.com/files/126854/Castor-Library-XXE-Disclosure.html
- http://seclists.org/fulldisclosure/2014/May/142
