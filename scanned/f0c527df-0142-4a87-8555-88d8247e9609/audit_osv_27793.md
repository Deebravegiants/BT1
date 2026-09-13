# [M] Element Android can be asked to share internal files.

## Summary
Severity: Medium
Advisory: CVE-2024-26132
Aliases: GHSA-8wj9-cx7h-pvm4
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-02-20
Source: https://osv.dev/vulnerability/CVE-2024-26132
Type: osv

## Details
Element Android is an Android Matrix Client. A third-party malicious application installed on the same phone can force Element Android, version 0.91.0 through 1.6.12, to share files stored under the `files` directory in the application's private data directory to an arbitrary room. The impact of the attack is reduced by the fact that the databases stored in this folder are encrypted. However, it contains some other potentially sensitive information, such as the FCM token. Forks of Element Android which have set `android:exported="false"` in the `AndroidManifest.xml` file for the `IncomingShareActivity` activity are not impacted. This issue is fixed in Element Android 1.6.12. There is no known workaround to mitigate the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26132.json
- https://github.com/element-hq/element-android/security/advisories/GHSA-8wj9-cx7h-pvm4
- https://nvd.nist.gov/vuln/detail/CVE-2024-26132
- https://github.com/element-hq/element-android/commit/8f9695a9a8d944cb9b92568cbd76578c51d32e07
- https://element.io/blog/security-release-element-android-1-6-12
