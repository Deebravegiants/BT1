# [M] BigBlueButton contains DoS via failed authToken validation

## Summary
Severity: Medium
Advisory: CVE-2022-41960
Aliases: GHSA-rgjp-3r74-g4cm
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2022-12-15
Source: https://osv.dev/vulnerability/CVE-2022-41960
Type: osv

## Details
BigBlueButton is an open source web conferencing system. Versions prior to 2.4.3, are subject to Insufficient Verification of Data Authenticity, resulting in Denial of Service. An attacker can make a Meteor call to `validateAuthToken` using a victim's userId, meetingId, and an invalid authToken. This forces the victim to leave the conference, because the resulting verification failure is also observed and handled by the victim's client. The attacker must be a participant in any meeting on the server. This issue is patched in version 2.4.3. There are no workarounds.

## References
- https://github.com/bigbluebutton/bigbluebutton/releases/tag/v2.4.3
- https://github.com/bigbluebutton/bigbluebutton/releases/tag/v2.5-alpha-1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41960.json
- https://github.com/bigbluebutton/bigbluebutton/security/advisories/GHSA-rgjp-3r74-g4cm
- https://nvd.nist.gov/vuln/detail/CVE-2022-41960
