# [H] Apache Directory Studio Command Injection

## Summary
Severity: High
Advisory: GHSA-p9qj-4rjp-j3w9
CVE: CVE-2015-5349
CWE: CWE-77
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-p9qj-4rjp-j3w9
Type: github-advisory

## Affected
- Maven: `org.apache.directory.studio:org.apache.directory.studio.ldapbrowser.core` — affected >=0 <2.0.0.v20151221-M10

## Details
The CSV export in Apache LDAP Studio and Apache Directory Studio before 2.0.0-M10 does not properly escape field values, which might allow attackers to execute arbitrary commands by leveraging a crafted LDAP entry that is interpreted as a formula when imported into a spreadsheet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5349
- https://github.com/apache/directory-studio/commit/ac57a26fcb98aa17fe9534575cf5fdad00a1c839
- https://directory.apache.org/studio/news.html
- https://github.com/apache/directory-studio
- https://lists.apache.org/thread.html/reb5443aaf781b364896ee9d7cf6e97fdc4f5a5174132c319252963b6@%3Ccommits.directory.apache.org%3E
- https://web.archive.org/web/20201209040832/http://www.securityfocus.com/archive/1/537225/100/0/threaded
