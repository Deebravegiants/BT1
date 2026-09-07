# [M] Athenz vulnerable to Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-9hg5-7hwc-v434
CVE: CVE-2019-6035
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9hg5-7hwc-v434
Type: github-advisory

## Affected
- Maven: `com.yahoo.athenz:athenz` — affected >=0 <1.8.25

## Details
Open redirect vulnerability in Athenz v1.8.24 and earlier allows remote attackers to redirect users to arbitrary web sites and conduct phishing attacks via a specially crafted page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-6035
- https://github.com/yahoo/athenz/pull/700
- https://github.com/AthenZ/athenz/commit/c4dc89b31fda501af45c20b33db620a077079744
- https://github.com/AthenZ/athenz
- http://jvn.jp/en/jp/JVN57070811/index.html
