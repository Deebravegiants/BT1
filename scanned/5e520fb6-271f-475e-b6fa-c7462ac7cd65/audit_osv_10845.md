# [H] CVE-2017-3189

## Summary
Severity: High
Advisory: CVE-2017-3189
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-24
Source: https://osv.dev/vulnerability/CVE-2017-3189
Type: osv

## Details
The dotCMS administration panel, versions 3.7.1 and earlier, "Push Publishing" feature in Enterprise Pro is vulnerable to arbitrary file upload. When "Bundle" tar.gz archives uploaded to the Push Publishing feature are decompressed, there are no checks on the types of files which the bundle contains. This vulnerability combined with the path traversal vulnerability (CVE-2017-3188) can lead to remote command execution with the permissions of the user running the dotCMS application. An unauthenticated remote attacker may perform actions with the dotCMS administrator panel with the same permissions of a victim user or execute arbitrary system commands with the permissions of the user running the dotCMS application.

## References
- http://www.securityfocus.com/bid/96616
- https://www.kb.cert.org/vuls/id/168699
