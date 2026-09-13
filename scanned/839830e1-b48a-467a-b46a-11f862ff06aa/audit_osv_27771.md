# [H] IDOR Vulnerability: Allowing Organization Owner to view the other Organizations API KEY and USERS

## Summary
Severity: High
Advisory: CVE-2024-25635
Aliases: GHSA-ffr5-g3qg-gp4f
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-19
Source: https://osv.dev/vulnerability/CVE-2024-25635
Type: osv

## Details
alf.io is an open source ticket reservation system. Prior to version 2.0-Mr-2402, organization owners can view the generated API KEY and USERS of other organization owners using the `http://192.168.26.128:8080/admin/api/users/<user_id>` endpoint, which exposes the details of the provided user ID. This may also expose the API KEY in the username of the user. Version 2.0-M4-2402 fixes this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25635.json
- https://github.com/alfio-event/alf.io/security/advisories/GHSA-ffr5-g3qg-gp4f
- https://nvd.nist.gov/vuln/detail/CVE-2024-25635
