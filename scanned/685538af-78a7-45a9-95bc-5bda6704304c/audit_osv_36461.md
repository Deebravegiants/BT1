# [M] OpenProject users can delete other user's session, causing them to be logged out

## Summary
Severity: Medium
Advisory: CVE-2026-23646
Aliases: GHSA-w422-xf8f-v4vp
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-19
Source: https://osv.dev/vulnerability/CVE-2026-23646
Type: osv

## Details
OpenProject is an open-source, web-based project management software. Users of OpenProject versions prior to 16.6.5 and 17.0.1 have the ability to view and end their active sessions via Account Settings → Sessions. When deleting a session, it was not properly checked if the session belongs to the user. As the ID that is used to identify these session objects use incremental integers, users could iterate requests using `DELETE /my/sessions/:id` and thus unauthenticate other users. Users did not have access to any sensitive information (like browser identifier, IP addresses, etc) of other users that are stored in the session. The problem was patched in OpenProject versions 16.6.5 and 17.0.1. No known workarounds are available as this does not require any permissions or other that can temporarily be disabled.

## References
- https://github.com/opf/openproject/releases/tag/v16.6.5
- https://github.com/opf/openproject/releases/tag/v17.0.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23646.json
- https://github.com/opf/openproject/security/advisories/GHSA-w422-xf8f-v4vp
- https://nvd.nist.gov/vuln/detail/CVE-2026-23646
