# [H] Uncontrolled Resource Consumption in jboss-remoting

## Summary
Severity: High
Advisory: GHSA-p6j8-hgv5-m35g
CVE: CVE-2020-35510
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-p6j8-hgv5-m35g
Type: github-advisory

## Affected
- Maven: `org.jboss.remoting:jboss-remoting` — affected >=0 <5.0.20.Final

## Details
A flaw was found in jboss-remoting in versions before 5.0.20.SP1-redhat-00001. A malicious attacker could cause threads to hold up forever in the EJB server by writing a sequence of bytes corresponding to the expected messages of a successful EJB client request, but omitting the ACK messages, or just tamper with jboss-remoting code, deleting the lines that send the ACK message from the EJB client code resulting in a denial of service. The highest threat from this vulnerability is to system availability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35510
- https://bugzilla.redhat.com/show_bug.cgi?id=1905796
