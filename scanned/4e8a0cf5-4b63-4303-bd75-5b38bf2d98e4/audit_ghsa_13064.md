# [M] OpenNMS privilege escalation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hf5p-f83x-5q2g
CVE: CVE-2023-40315
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:H/PR:H/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2023-08-17
Source: https://github.com/advisories/GHSA-hf5p-f83x-5q2g
Type: github-advisory

## Affected
- Maven: `org.opennms:opennms-webapp-rest` — affected >=31.0.8 <32.0.2

## Details
In OpenNMS Horizon 31.0.8 and versions earlier than 32.0.2 and related Meridian versions, any user that has the ROLE_FILESYSTEM_EDITOR can easily escalate their privileges to ROLE_ADMIN or any other role. The solution is to upgrade to Meridian 2023.1.5 or Horizon 32.0.2 or newer. Meridian and Horizon installation instructions state that they are intended for installation within an organization's private networks and should not be directly accessible from the Internet. OpenNMS thanks Erik Wynter for reporting this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40315
- https://github.com/OpenNMS/opennms/pull/6250
- https://github.com/OpenNMS/opennms/commit/f2caf7d0b9db58b59e98506490aaca37fbf243b6
- https://docs.opennms.com/meridian/2023/releasenotes/changelog.html#releasenotes-changelog-Meridian-2023.1.5
- https://github.com/OpenNMS/opennms
