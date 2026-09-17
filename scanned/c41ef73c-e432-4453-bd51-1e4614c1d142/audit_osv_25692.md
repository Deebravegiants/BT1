# [H] Arbitrary URL load in Android WebView in `MyActivity.kt` in Home Assistant Companion for Android

## Summary
Severity: High
Advisory: CVE-2023-41898
Aliases: GHSA-jvpm-q3hq-86rg
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2023-10-19
Source: https://osv.dev/vulnerability/CVE-2023-41898
Type: osv

## Details
Home assistant is an open source home automation. The Home Assistant Companion for Android app up to version 2023.8.2 is vulnerable to arbitrary URL loading in a WebView. This enables all sorts of attacks, including arbitrary JavaScript execution, limited native code execution, and credential theft. This issue has been patched in version 2023.9.2 and all users are advised to upgrade. There are no known workarounds for this vulnerability. This issue is also tracked as GitHub Security Lab (GHSL) Vulnerability Report: `GHSL-2023-142`.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/41xxx/CVE-2023-41898.json
- https://github.com/home-assistant/core/security/advisories/GHSA-jvpm-q3hq-86rg
- https://nvd.nist.gov/vuln/detail/CVE-2023-41898
