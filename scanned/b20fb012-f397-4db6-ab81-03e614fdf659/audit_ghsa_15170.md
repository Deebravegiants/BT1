# [M] react-native-mmkv Insertion of Sensitive Information into Log File vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4jh3-6jhv-2mgp
CVE: CVE-2024-21668
CWE: CWE-532
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-09
Source: https://github.com/advisories/GHSA-4jh3-6jhv-2mgp
Type: github-advisory

## Affected
- npm: `react-native-mmkv` — affected >=0 <2.11.0

## Details
## Summary
Before version [v2.11.0](https://github.com/mrousavy/react-native-mmkv/releases/tag/v2.11.0), the react-native-mmkv logged the optional encryption key for the MMKV database into the Android system log. The key can be obtained by anyone with access to the Android Debugging Bridge (ADB) if it is enabled in the phone settings. This bug is not present on iOS devices.

## Details
The bridge for communicating between JS code and native code on Android logs the encryption key. This was fixed in commit [a8995cc](https://github.com/mrousavy/react-native-mmkv/commit/a8995ccb7184281f7d168bad3e9987c9bd05f00d) by only logging whether encryption is used.

## Impact
The encryption of an MMKV database protects data from higher privilege processes on the phone that can access the app storage. Additionally, if data in the app's storage is encrypted, it is also encrypted in potential backups.
By logging the encryption secret to the system logs, attackers can trivially recover the secret by enabling ADB and undermining an app's thread model.

The bug was discovered and fixed by somebody else. Not me. I'm just reporting this so users of react-native-mmkv upgrade the dependency.

## References
- https://github.com/mrousavy/react-native-mmkv/security/advisories/GHSA-4jh3-6jhv-2mgp
- https://nvd.nist.gov/vuln/detail/CVE-2024-21668
- https://github.com/mrousavy/react-native-mmkv/commit/a8995ccb7184281f7d168bad3e9987c9bd05f00d
- https://github.com/mrousavy/react-native-mmkv
- https://github.com/mrousavy/react-native-mmkv/releases/tag/v2.11.0
