# [M] CORS misconfiguration in socket.io

## Summary
Severity: Medium
Advisory: GHSA-fxwf-4rqh-v8g3
CVE: CVE-2020-28481
CWE: CWE-346, CWE-453
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-01-20
Source: https://github.com/advisories/GHSA-fxwf-4rqh-v8g3
Type: github-advisory

## Affected
- npm: `socket.io` — affected >=0 <2.4.0

## Details
The package socket.io before 2.4.0 are vulnerable to Insecure Defaults due to CORS Misconfiguration. All domains are whitelisted by default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28481
- https://github.com/socketio/socket.io/issues/3671
- https://github.com/socketio/socket.io/commit/f78a575f66ab693c3ea96ea88429ddb1a44c86c7
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-1056358
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1056357
- https://snyk.io/vuln/SNYK-JS-SOCKETIO-1024859
