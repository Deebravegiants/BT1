# [H] BigBlueButton: Insecure Randomness allows to guess user's conference session token and impersonate them

## Summary
Severity: High
Advisory: CVE-2026-46351
Aliases: GHSA-7959-pf2v-xc4h
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-46351
Type: osv

## Details
BigBlueButton is an open-source virtual classroom. Prior to 3.0.21, bbb-web generated conference sessionToken values with insufficiently secure randomness in bbb-common-web/src/main/java/org/bigbluebutton/api/Util.java and bigbluebutton-web/grails-app/controllers/org/bigbluebutton/web/controllers/ApiController.groovy, allowing a session user to predict other users' conference session tokens and impersonate them. This issue is fixed in version 3.0.21.

## References
- https://github.com/bigbluebutton/bigbluebutton/releases/tag/v3.0.21
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46351.json
- https://github.com/bigbluebutton/bigbluebutton/security/advisories/GHSA-7959-pf2v-xc4h
- https://nvd.nist.gov/vuln/detail/CVE-2026-46351
- https://github.com/bigbluebutton/bigbluebutton/commit/8457886c248aeba5597ee8749267602d6d117e98
