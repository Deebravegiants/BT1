# [M] Expo on iOS is insecure due incorrect security attribute application

## Summary
Severity: Medium
Advisory: GHSA-rwx9-wqj8-vr77
CVE: CVE-2020-24653
Ecosystem: npm
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rwx9-wqj8-vr77
Type: github-advisory

## Affected
- npm: `expo` — affected >=0 <9.1.0

## Details
secure-store in Expo through 9.1.0 on iOS provides the insecure kSecAttrAccessibleAlwaysThisDeviceOnly policy when WHEN_UNLOCKED_THIS_DEVICE_ONLY is used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-24653
- https://github.com/expo/expo/pull/9264
- https://github.com/expo/expo/commit/1d82bf07fae2c96273e9189997e521359cffc1a9#diff-5b2820f378da980bd8a8185e2e1b2f9ce085d834534483f29c67932f282cc5c9
- https://github.com/expo/expo
- https://github.com/expo/expo/blob/main/packages/expo-secure-store/CHANGELOG.md
