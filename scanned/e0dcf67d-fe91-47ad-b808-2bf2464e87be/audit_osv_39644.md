# [H] BigBlueButton: Unauthenticated Session Hijack via Exposed /bigbluebutton/api/handleJoinExistingUser

## Summary
Severity: High
Advisory: CVE-2026-46355
Aliases: GHSA-38fw-2gq7-ccgr
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-46355
Type: osv

## Details
BigBlueButton is an open-source virtual classroom. Prior to 3.0.23, BigBlueButton exposed /bigbluebutton/api/handleJoinExistingUser through bigbluebutton-web/grails-app/controllers/org/bigbluebutton/web/controllers/ApiController.groovy. A requester able to supply an existingUserID for an active participant could reuse that participant's session and impersonate the participant in the same meeting because handleJoinExistingUser was a routable controller action rather than a private helper. This issue is fixed in version 3.0.23.

## References
- https://github.com/bigbluebutton/bigbluebutton/releases/tag/v3.0.23
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46355.json
- https://github.com/bigbluebutton/bigbluebutton/security/advisories/GHSA-38fw-2gq7-ccgr
- https://nvd.nist.gov/vuln/detail/CVE-2026-46355
- https://github.com/bigbluebutton/bigbluebutton/commit/972b04e474e195cbd708b5b3f0485fe528a1a85b
