# [M] React Native Sms User Consent Intent Redirection Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-r956-2553-vvhr
CVE: CVE-2021-4438
CWE: CWE-926
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-04-07
Source: https://github.com/advisories/GHSA-r956-2553-vvhr
Type: github-advisory

## Affected
- npm: `@kyivstarteam/react-native-sms-user-consent` — affected >=0 <1.1.5

## Details
A vulnerability, which was classified as critical, has been found in kyivstarteam react-native-sms-user-consent up to 1.1.4 on Android. Affected by this issue is the function `registerReceiver` of the file `android/src/main/java/ua/kyivstar/reactnativesmsuserconsent/SmsUserConsentModule.kt`. The manipulation leads to improper export of android application components. Attacking locally is a requirement. Upgrading to version 1.1.5 is able to address this issue. The name of the patch is 5423dcb0cd3e4d573b5520a71fa08aa279e4c3c7. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-259508.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4438
- https://github.com/kyivstarteam/react-native-sms-user-consent/pull/4
- https://github.com/kyivstarteam/react-native-sms-user-consent/commit/5423dcb0cd3e4d573b5520a71fa08aa279e4c3c7
- https://github.com/kyivstarteam/react-native-sms-user-consent
- https://github.com/kyivstarteam/react-native-sms-user-consent/releases/tag/1.1.5
- https://vuldb.com/?ctiid.259508
- https://vuldb.com/?id.259508
