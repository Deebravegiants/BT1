# [H] XML External Entity Reference in Apache Cayenne

## Summary
Severity: High
Advisory: GHSA-85hw-w436-c725
CVE: CVE-2018-11758
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-85hw-w436-c725
Type: github-advisory

## Affected
- Maven: `org.apache.cayenne:cayenne-parent` — affected >=0 <3.1.3
- Maven: `org.apache.cayenne:cayenne-parent` — affected >=4.0 <4.1

## Details
This affects Apache Cayenne 4.1.M1, 3.2.M1, 4.0.M2 to 4.0.M5, 4.0.B1, 4.0.B2, 4.0.RC1, 3.1, 3.1.1, 3.1.2. CayenneModeler is a desktop GUI tool shipped with Apache Cayenne and intended for editing Cayenne ORM models stored as XML files. If an attacker tricks a user of CayenneModeler into opening a malicious XML file, the attacker will be able to instruct the XML parser built into CayenneModeler to transfer files from a local machine to a remote machine controlled by the attacker. The cause of the issue is XML parser processing XML External Entity (XXE) declarations included in XML. The vulnerability is addressed in Cayenne by disabling XXE processing in all operations that require XML parsing.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11758
- https://lists.apache.org/thread.html/ed60a4d329be3c722f105317ca883986dfcd17615c70d1df87f4528c@%3Cuser.cayenne.apache.org%3E
- apache/cayenne
