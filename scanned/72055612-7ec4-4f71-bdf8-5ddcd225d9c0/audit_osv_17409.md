# [C] CVE-2020-15097

## Summary
Severity: Critical
Advisory: CVE-2020-15097
Aliases: GHSA-7557-4v29-rqw6
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-02-02
Source: https://osv.dev/vulnerability/CVE-2020-15097
Type: osv

## Details
loklak is an open-source server application which is able to collect messages from various sources, including twitter. The server contains a search index and a peer-to-peer index sharing interface. All messages are stored in an elasticsearch index. In loklak less than or equal to commit 5f48476, a path traversal vulnerability exists. Insufficient input validation in the APIs exposed by the loklak server allowed a directory traversal vulnerability. Any admin configuration and files readable by the app available on the hosted file system can be retrieved by the attacker. Furthermore, user-controlled content could be written to any admin config and files readable by the application. This has been patched in commit 50dd692. Users will need to upgrade their hosted instances of loklak to not be vulnerable to this exploit.

## References
- https://github.com/loklak/loklak_server/security/advisories/GHSA-7557-4v29-rqw6
- https://github.com/loklak/loklak_server/commit/50dd69230d3cd71dab0bfa7156682ffeca8ed8b9
