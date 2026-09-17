# [H] OneSignal repository github action command injection

## Summary
Severity: High
Advisory: CVE-2023-28430
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N)
Published: 2023-03-27
Source: https://osv.dev/vulnerability/CVE-2023-28430
Type: osv

## Details
OneSignal is an email, sms, push notification, and in-app message service for mobile apps.The Zapier.yml workflow is triggered on issues (types: [closed]) (i.e., when an Issue is closed). The workflow starts with full write-permissions GitHub repository token since the default workflow permissions on Organization/Repository level are set to read-write. This workflow runs the following step with data controlled by the comment `(${{ github.event.issue.title }} – the full title of the Issue)`, allowing an attacker to take over the GitHub Runner and run custom commands, potentially stealing any secret (if used), or altering the repository. This issue was found with CodeQL using javascript’s Expression injection in Actions query. This issue has been addressed in the repositories github action. No actions are required by users. This issue is also tracked as `GHSL-2023-051`.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28430.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-28430
- https://securitylab.github.com/advisories/GHSL-2023-051_React_Native_OneSignal_SDK/
- https://github.com/OneSignal/react-native-onesignal/commit/4a66f4237fb51dcc2236889038d488cd49b0f433
- https://github.com/OneSignal/react-native-onesignal/commit/4e43bda4ce1eb395f36bb8a5640002523c051085
