# [C] Apache Linkis Unrestricted File Upload vulnerability

## Summary
Severity: Critical
Advisory: GHSA-x84r-jrqm-3hj8
CVE: CVE-2023-27602
CWE: CWE-434
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-x84r-jrqm-3hj8
Type: github-advisory

## Affected
- Maven: `org.apache.linkis:linkis` — affected >=0 <1.3.2

## Details
In Apache Linkis <=1.3.1, The PublicService module uploads files without restrictions on the path to the uploaded files, and file types.

We recommend users upgrade the version of Linkis to version 1.3.2. 

For versions <=1.3.1, we suggest turning on the file path check switch in linkis.properties

`wds.linkis.workspace.filesystem.owner.check=true`
`wds.linkis.workspace.filesystem.path.check=true`

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27602
- https://github.com/apache/linkis
- https://lists.apache.org/thread/wt70jfc0yfs6s5g0wg5dr5klnc48nsp1
- http://www.openwall.com/lists/oss-security/2023/04/10/1
- http://www.openwall.com/lists/oss-security/2023/04/18/4
- http://www.openwall.com/lists/oss-security/2023/04/19/3
