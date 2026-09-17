# [H] Square OkHttp can accept the wrong certificate

## Summary
Severity: High
Advisory: GHSA-3cqm-mf7h-prrj
CVE: CVE-2021-0341
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-3cqm-mf7h-prrj
Type: github-advisory

## Affected
- Maven: `com.squareup.okhttp3:okhttp` — affected >=0 <4.9.2

## Details
In verifyHostName of OkHostnameVerifier.java, there is a possible way to accept a certificate for the wrong domain due to improperly used crypto. This could lead to remote information disclosure with no additional execution privileges needed. User interaction is not needed for exploitation. Product: AndroidVersions: Android-8.1 Android-9 Android-10 Android-11 Android ID: A-171980069

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-0341
- https://github.com/square/okhttp/issues/6724
- https://github.com/square/okhttp/pull/6741
- https://github.com/square/okhttp/commit/f574ea2f5259d9040f264ddeb582fb1ce563f10c
- https://github.com/square/okhttp
- https://source.android.com/security/bulletin/2021-02-01
