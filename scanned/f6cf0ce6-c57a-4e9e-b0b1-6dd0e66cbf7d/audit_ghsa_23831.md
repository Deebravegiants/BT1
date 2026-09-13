# [C] Apache Storm remote code execution vulnerability

## Summary
Severity: Critical
Advisory: GHSA-cg5h-q983-4rww
CVE: CVE-2015-3188
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-cg5h-q983-4rww
Type: github-advisory

## Affected
- Maven: `org.apache.storm:storm` — affected >=0.10.0-beta <0.10.0-beta1

## Details
The UI daemon in Apache Storm 0.10.0-beta allows remote users to run arbitrary code as the user running the web server. With kerberos authentication this could allow impersonation of arbitrary users on other systems, including HDFS and HBase.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3188
- https://github.com/apache/storm/blob/v0.10.0-beta1/SECURITY.md
- https://github.com/apache/storm/blob/v0.10.0-beta1/STORM-UI-REST-API.md
- https://web.archive.org/web/20151014213052/http://www.securitytracker.com/id/1032695
- https://web.archive.org/web/20171202122914/http://www.securityfocus.com/archive/1/535804/100/0/threaded
- http://packetstormsecurity.com/files/132417/Apache-Storm-0.10.0-beta-Code-Execution.html
