# [M] Android WebView Universal Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-36j3-xxf7-4pqg
CVE: CVE-2020-6506
CWE: CWE-79, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2020-10-02
Source: https://github.com/advisories/GHSA-36j3-xxf7-4pqg
Type: github-advisory

## Affected
- npm: `react-native-webview` — affected >=0 <11.0.0

## Details
A universal cross-site scripting (UXSS) vulnerability, CVE-2020-6506 (https://crbug.com/1083819), has been identified in the Android WebView system component, which allows cross-origin iframes to execute arbitrary JavaScript in the top-level document. This vulnerability affects React Native apps which use a `react-native-webview` that allows navigation to arbitrary URLs, and when that app runs on systems with an Android WebView version prior to 83.0.4103.106.

## Pending mitigation

Ensure users update their Android WebView system component via the Google Play Store to 83.0.4103.106 or higher to avoid this UXSS. 'react-native-webview' is working on a mitigation but it could take some time.

### References

https://alesandroortiz.com/articles/uxss-android-webview-cve-2020-6506/

## References
- https://github.com/react-native-community/react-native-webview/security/advisories/GHSA-36j3-xxf7-4pqg
- https://github.com/react-native-webview/react-native-webview/security/advisories/GHSA-36j3-xxf7-4pqg
- https://nvd.nist.gov/vuln/detail/CVE-2020-6506
- https://github.com/react-native-webview/react-native-webview/pull/1747
- https://www.npmjs.com/advisories/1560
- https://security.gentoo.org/glsa/202101-30
- https://security.gentoo.org/glsa/202007-08
- https://lists.apache.org/thread.html/rf082834ad237f78a63671aec0cef8874f9232b7614529cc3d3e304c5@%3Ccommits.cordova.apache.org%3E
- https://lists.apache.org/thread.html/rc81e12fc9287f8743d59099b1af40f968f1cfec9eac98a63c2c62c69@%3Cissues.cordova.apache.org%3E
- https://lists.apache.org/thread.html/rc0ebe639927fa09e222aa56bf5ad6e700218f334ecc6ba9da4397728@%3Cissues.cordova.apache.org%3E
- https://lists.apache.org/thread.html/ra58733fbb88d5c513b3f14a14850083d506b9129103e0ab433c3f680@%3Cissues.cordova.apache.org%3E
- https://lists.apache.org/thread.html/r2769c33da7f7ece7e4e31837c1e1839d6657c7c13bb8d228670b8da0@%3Cissues.cordova.apache.org%3E
- https://lists.apache.org/thread.html/r1eadf38b38ee20405811958c8a01f78d6b28e058c84c9fa6c1a8663d@%3Cissues.cordova.apache.org%3E
- https://lists.apache.org/thread.html/r1ab80f8591d5c2147898076e3945dad1c897513630aabec556883275@%3Cissues.cordova.apache.org%3E
- https://github.com/react-native-webview/react-native-webview/releases/tag/v11.0.0
- https://github.com/react-native-community/react-native-webview
- https://crbug.com/1083819
- https://chromereleases.googleblog.com/2020/06/stable-channel-update-for-desktop_15.html
- https://alesandroortiz.com/articles/uxss-android-webview-cve-2020-6506
