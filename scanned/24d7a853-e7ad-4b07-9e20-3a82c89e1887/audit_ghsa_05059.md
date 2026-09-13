# [C] Cordova Plugin InAppBrowser: iOS: Arbitrary Cordova callback IDs can be dispatched without validation from InAppBrowser WebViews.

## Summary
Severity: Critical
Advisory: GHSA-q42j-x8rq-pjg6
CVE: CVE-2026-47430
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-q42j-x8rq-pjg6
Type: github-advisory

## Affected
- npm: `cordova-plugin-inappbrowser` — affected >=0 <6.0.1

## Details
## Summary

The iOS implementation of `cordova-plugin-inappbrowser` passes the `id` field from a `WKScriptMessage` body to `commandDelegate sendPluginResult:callbackId:` with no format validation (`CDVWKInAppBrowser.m:560–574`). Any web content loaded inside the InAppBrowser can fire any pending Cordova callback in the host app by posting a message whose `id` field is a guessable or enumerated callback identifier. An attack abusing this weakness must be tailored to the specific plugins and callback IDs the host app uses. Though an attacker with knowledge of common Cordova plugin configurations could craft reusable payloads targeting widely-adopted plugins.


## Impact

An unauthenticated remote attacker who controls content displayed in the InAppBrowser — via a URL the app opens (OAuth redirect, marketing link, deep-link target) or a network interception — can call `window.webkit.messageHandlers.cordova_iab.postMessage({id: '<victim-callback-id>', d: '...'})` to fire callbacks belonging to any other installed Cordova plugin (Camera, Contacts, File, Geolocation). Cordova callback IDs follow the predictable format `<PluginName><sequential-integer>`, making enumeration feasible. Successful exploitation allows the attacker to spoof plugin results across trust boundaries — for example, injecting a forged camera approval, a fabricated contacts list, or a crafted file-read response.

This issue affects Cordova Plugin InAppBrowser: from 3.1.0 through 6.0.0.

Users are recommended to upgrade to version 6.0.1, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-47430
- https://github.com/apache/cordova-plugin-inappbrowser
- https://lists.apache.org/thread/sb539nss3b0545wnyt1pbh7zgwjvz2qq
- http://www.openwall.com/lists/oss-security/2026/06/07/1
