# [H] Path Traversal in cordova-plugin-ionic-webview

## Summary
Severity: High
Advisory: GHSA-xwjh-cp99-cj8q
CVE: CVE-2018-16202
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2019-02-12
Source: https://github.com/advisories/GHSA-xwjh-cp99-cj8q
Type: github-advisory

## Affected
- npm: `cordova-plugin-ionic-webview` — affected >=0 <2.2.0

## Details
Versions of `cordova-plugin-ionic-webview` prior to 2.2.0 are vulnerable to Path Traversal, allowing attackers access to OS local files that should be inaccessible by third-party applications.  The package launches a webserver listening on http://localhost:8080 without restricting access of the app itself, thus escaping the iOS application sandbox and accessing local files.


## Recommendation

Upgrade to version 2.2.0

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16202
- https://github.com/advisories/GHSA-xwjh-cp99-cj8q
- https://github.com/ionic-team/cordova-plugin-ionic-webview
- https://jvn.jp/en/jp/JVN69812763/index.html
- https://www.npmjs.com/advisories/746
- http://jvn.jp/en/jp/JVN60497148/index.html
