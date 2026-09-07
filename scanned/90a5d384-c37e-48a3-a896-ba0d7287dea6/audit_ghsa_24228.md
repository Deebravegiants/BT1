# [M] Improper Neutralization of Input During Web Page Generation in Apache Axis2

## Summary
Severity: Medium
Advisory: GHSA-23x8-j7hm-5xwf
CVE: CVE-2010-2103
CWE: CWE-79
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-23x8-j7hm-5xwf
Type: github-advisory

## Affected
- Maven: `org.apache.axis2.wso2:axis2` — affected >=1.4.1 <1.6.0

## Details
Cross-site scripting (XSS) vulnerability in axis2-admin/axis2-admin/engagingglobally in the administration console in Apache Axis2/Java 1.4.1, 1.5.1, and possibly other versions, as used in SAP Business Objects 12, 3com IMC, and possibly other products, allows remote attackers to inject arbitrary web script or HTML via the modules parameter.  NOTE: some of these details are obtained from third party information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-2103
- https://exchange.xforce.ibmcloud.com/vulnerabilities/58790
- https://kb.juniper.net/KB27373
- http://osvdb.org/64844
- http://spl0it.org/files/talks/source_barcelona10/Hacking%20SAP%20BusinessObjects.pdf
- http://www.exploit-db.com/exploits/12689
- http://www.procheckup.com/vulnerability_manager/vulnerabilities/pr10-03
