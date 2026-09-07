# [H] Exposure of Sensitive Information to an Unauthorized Actor in org.xwiki.platform:xwiki-platform-office-viewer

## Summary
Severity: High
Advisory: GHSA-m3c3-9qj7-7xmx
CVE: CVE-2023-29517
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-04-20
Source: https://github.com/advisories/GHSA-m3c3-9qj7-7xmx
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-office-viewer` — affected >=2.5-milestone-2 <13.10.11
- Maven: `org.xwiki.platform:xwiki-platform-office-viewer` — affected >=14.0-rc-1 <14.4.8
- Maven: `org.xwiki.platform:xwiki-platform-office-viewer` — affected >=14.5 <14.10.1

## Details
### Impact

The office document viewer macro was allowing anyone to see any file content from the hosting server, provided that the office server was connected and depending on the permissions of the user running the servlet engine (e.g. tomcat) running XWiki. The same vulnerability also allowed to perform internal requests to resources from the hosting server.

### Patches

The problem has been patched in XWiki 13.10.11, 14.10.1, 14.4.8, 15.0-rc-1.

### Workarounds

It might be possible to workaround this vulnerability by running XWiki in a sandbox with a user with very low privileges on the machine, now to run a servlet engine the user will always need access to some files, so in any case this workaround won't protect all files to be accessed.

### References

  * Original jira ticket: https://jira.xwiki.org/browse/XWIKI-20447
  * Jira ticket related to another exploit using same root cause: https://jira.xwiki.org/browse/XWIKI-20324
  * Jira ticket related to the possibility to exploit the same vulnerability to perform internal requests: https://jira.xwiki.org/browse/XWIKI-20449

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-m3c3-9qj7-7xmx
- https://nvd.nist.gov/vuln/detail/CVE-2023-29517
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20324
- https://jira.xwiki.org/browse/XWIKI-20447
- https://jira.xwiki.org/browse/XWIKI-20449
