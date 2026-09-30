# [M] Improper Input Validation in Apache Archiva

## Summary
Severity: Medium
Advisory: GHSA-jxgm-9f58-w4xp
CVE: CVE-2019-0214
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-05-14
Source: https://github.com/advisories/GHSA-jxgm-9f58-w4xp
Type: github-advisory

## Affected
- Maven: `org.apache.archiva:archiva` — affected >=2.2.0 <2.2.4

## Details
In Apache Archiva 2.0.0 - 2.2.3, it is possible to write files to the archiva server at arbitrary locations by using the artifact upload mechanism. Existing files can be overwritten, if the archiva run user has appropriate permission on the filesystem for the target file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0214
- https://lists.apache.org/thread.html/18b670afc2f83034f47ebeb2f797c350fe60f1f2b33c95b95f467ef8@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/239349b6dd8f66cf87a70c287b03af451dea158b776d3dfc550b4f0e@%3Cusers.maven.apache.org%3E
- https://lists.apache.org/thread.html/5851cb0214f22ba681fb445870eeb6b01afd1fb614e45a22978d7dda@%3Cusers.archiva.apache.org%3E
- https://lists.apache.org/thread.html/ada0052409d8a4a8c4eb2c7fd6b9cd9423bc753d5fce87eb826662fb@%3Cissues.archiva.apache.org%3E
- https://seclists.org/bugtraq/2019/Apr/48
- http://archiva.apache.org/security.html#CVE-2019-0214
- http://packetstormsecurity.com/files/152684/Apache-Archiva-2.2.3-File-Write-Delete.html
- http://www.openwall.com/lists/oss-security/2019/04/30/8
- http://www.securityfocus.com/bid/108124
