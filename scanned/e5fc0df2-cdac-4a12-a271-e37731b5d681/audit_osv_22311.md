# [M] Possible Injection in Nextcloud Server

## Summary
Severity: Medium
Advisory: CVE-2022-24888
Aliases: GHSA-w3h6-p64h-q9jp
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2022-04-27
Source: https://osv.dev/vulnerability/CVE-2022-24888
Type: osv

## Details
Nextcloud Server is the file server software for Nextcloud, a self-hosted productivity platform. Prior to versions 20.0.14.4, 21.0.8, 22.2.4, and 23.0.1, it is possible to create files and folders that have leading and trailing \n, \r, \t, and \v characters. The server rejects files and folders that have these characters in the middle of their names, so this might be an opportunity for injection. This issue is fixed in versions 20.0.14.4, 21.0.8, 22.2.4, and 23.0.1. There are currently no known workarounds.

## References
- https://hackerone.com/reports/1402249
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24888.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-w3h6-p64h-q9jp
- https://nvd.nist.gov/vuln/detail/CVE-2022-24888
- https://security.gentoo.org/glsa/202208-17
- https://github.com/nextcloud/server/pull/29895
