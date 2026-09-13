# [M] wire-server vulnerable to unauthorized removal of Bots from Conversations

## Summary
Severity: Medium
Advisory: CVE-2023-22737
Aliases: GHSA-xmjc-c6w3-pcp4
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-27
Source: https://osv.dev/vulnerability/CVE-2023-22737
Type: osv

## Details
wire-server provides back end services for Wire, a team communication and collaboration platform. Prior to version 2022-12-09, every member of a Conversation can remove a Bot from a Conversation due to a missing permissions check. Only Conversation admins should be able to remove Bots. Regular Conversations are not allowed to do so. The issue is fixed in wire-server 2022-12-09 and is already deployed on all Wire managed services. On-premise instances of wire-server need to be updated to 2022-12-09/Chart 4.29.0, so that their backends are no longer affected. There are no known workarounds.

## References
- https://github.com/wireapp/wire-server/releases/tag/v2022-12-09
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/22xxx/CVE-2023-22737.json
- https://github.com/wireapp/wire-server/security/advisories/GHSA-xmjc-c6w3-pcp4
- https://nvd.nist.gov/vuln/detail/CVE-2023-22737
- https://github.com/wireapp/wire-server/commit/494a6881f5895d4ed9e5d011455242be0d5e6223
- https://github.com/wireapp/wire-server/pull/2870
