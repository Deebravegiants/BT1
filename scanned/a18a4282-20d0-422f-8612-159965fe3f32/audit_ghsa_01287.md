# [H] Information Exposure in cordova-android

## Summary
Severity: High
Advisory: GHSA-gwpf-62xp-vrg6
CVE: CVE-2016-6799
CWE: CWE-532
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-09-11
Source: https://github.com/advisories/GHSA-gwpf-62xp-vrg6
Type: github-advisory

## Affected
- npm: `cordova-android` — affected >=0 <6.0.0

## Details
Versions of `cordova-android` prior to 6.0.0 are vulnerable to Information Exposure through log files. The application calls methods of the Log class. Messages passed to these methods (Log.v(), Log.d(), Log.i(), Log.w(), and Log.e()) are stored in a series of circular buffers on the device. By default, a maximum of four 16 KB rotated logs are kept in addition to the current log. The logged data can be read using Logcat on the device. When using platforms prior to Android 4.1 (Jelly Bean), the log data is not sandboxed per application; any application installed on the device has the capability to read data logged by other applications.


## Recommendation

Upgrade to version 6.0.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6799
- https://github.com/apache/cordova-android/commit/4a0a7bc424fae14c9689f4a8a2dc250ae3a47f82
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-6799
- https://github.com/apache/cordova-android
- https://lists.apache.org/thread.html/1f3e7b0319d64b455f73616f572acee36fbca31f87f5b2e509c45b69@%3Cdev.cordova.apache.org%3E
- https://snyk.io/vuln/SNYK-JS-CORDOVAANDROID-174935
- https://www.npmjs.com/advisories/964
- http://www.securityfocus.com/bid/98365
