# [M] Improper Access Control in Apache WSS4J

## Summary
Severity: Medium
Advisory: GHSA-6r5v-hp32-fjqw
CVE: CVE-2015-0227
CWE: CWE-284
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-6r5v-hp32-fjqw
Type: github-advisory

## Affected
- Maven: `org.apache.ws.security:wss4j` — affected >=0 <1.6.17
- Maven: `org.apache.ws.security:wss4j` — affected >=2.0.0 <2.02
- Maven: `wss4j:wss4j` — affected >=0 <1.6.17

## Details
Apache WSS4J before 1.6.17 and 2.x before 2.0.2 allows remote attackers to bypass the requireSignedEncryptedDataElements configuration via a vectors related to "wrapping attacks."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-0227
- https://exchange.xforce.ibmcloud.com/vulnerabilities/100837
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbgn03900en_us
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
- http://rhn.redhat.com/errata/RHSA-2015-0773.html
- http://rhn.redhat.com/errata/RHSA-2015-0846.html
- http://rhn.redhat.com/errata/RHSA-2015-0847.html
- http://rhn.redhat.com/errata/RHSA-2015-0848.html
- http://rhn.redhat.com/errata/RHSA-2015-0849.html
- http://rhn.redhat.com/errata/RHSA-2015-1176.html
- http://rhn.redhat.com/errata/RHSA-2015-1177.html
- http://ws.apache.org/wss4j/advisories/CVE-2015-0227.txt.asc
