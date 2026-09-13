# [H] Remote code execution via specially crafted script settings in SABnzbd

## Summary
Severity: High
Advisory: CVE-2023-34237
Aliases: GHSA-hhgh-xgh3-985r
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-07
Source: https://osv.dev/vulnerability/CVE-2023-34237
Type: osv

## Details
SABnzbd is an open source automated Usenet download tool. A design flaw was discovered in SABnzbd that could allow remote code execution. Manipulating the Parameters setting in the Notification Script functionality allows code execution with the privileges of the SABnzbd process. Exploiting the vulnerabilities requires access to the web interface. Remote exploitation is possible if users[exposed their setup to the internet or other untrusted networks without setting a username/password. By default SABnzbd is only accessible from `localhost`, with no authentication required for the web interface. This issue has been patched in commits `e3a722` and `422b4f` which have been included in the 4.0.2 release. Users are advised to upgrade. Users unable to upgrade should ensure that a username and password have been set if their instance is web accessible.

## References
- https://sabnzbd.org/wiki/configuration/4.0/general
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34237.json
- https://github.com/sabnzbd/sabnzbd/security/advisories/GHSA-hhgh-xgh3-985r
- https://nvd.nist.gov/vuln/detail/CVE-2023-34237
- https://security.gentoo.org/glsa/202312-11
- https://github.com/sabnzbd/sabnzbd/commit/422b4fce7bfd56e95a315be0400cdfdc585df7cc
- https://github.com/sabnzbd/sabnzbd/commit/e3a722664819d1c7c8fab97144cc299b1c18b429
