# [M] Remote Code Execution and download tracking in Mintegral SDK

## Summary
Severity: Medium
Advisory: GHSA-c6p9-24rc-jr5h
CVE: CVE-2020-7744
CWE: CWE-319
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2021-04-22
Source: https://github.com/advisories/GHSA-c6p9-24rc-jr5h
Type: github-advisory

## Affected
- Maven: `com.mintegral.msdk:alphab` — affected >=0

## Details
"This affects all versions of package com.mintegral.msdk:alphab. The Android SDK distributed by the company contains malicious functionality in this module that tracks: 1. Downloads from Google urls either within Google apps or via browser including file downloads, e-mail attachments and Google Docs links. 2. All apk downloads, either organic or not. Mintegral listens to download events in Android's download manager and detects if the downloaded file's url contains: a. google.com or comes from a Google app (the com.android.vending package) b. Ends with .apk for apk downloads In both cases, the module sends the captured data back to Mintegral's servers. Note that the malicious functionality keeps running even if the app is currently not in focus (running in the background)."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7744
- https://snyk.io/blog/remote-code-execution-rce-sourmint
- https://snyk.io/research/sour-mint-malicious-sdk
- https://snyk.io/vuln/SNYK-JAVA-COMMINTEGRALMSDK-1018714
