# [M] Element iOS is vulnerable due to missing decoration for events decrypted with untrusted Megolm sessions

## Summary
Severity: Medium
Advisory: CVE-2022-41904
Aliases: GHSA-fm8m-99j7-323g
CVSS: 6.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N)
Published: 2022-11-11
Source: https://osv.dev/vulnerability/CVE-2022-41904
Type: osv

## Details
Element iOS is an iOS Matrix client provided by Element. It is based on MatrixSDK. Prior to version 1.9.7, events encrypted using Megolm for which trust could not be established did not get decorated accordingly (with warning shields). Therefore a malicious homeserver could inject messages into the room without the user being alerted that the messages were not sent by a verified group member, even if the user has previously verified all group members. This issue has been patched in Element iOS 1.9.7. There are currently no known workarounds.

## References
- https://github.com/vector-im/element-ios/releases/tag/v1.9.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41904.json
- https://github.com/vector-im/element-ios/security/advisories/GHSA-fm8m-99j7-323g
- https://nvd.nist.gov/vuln/detail/CVE-2022-41904
