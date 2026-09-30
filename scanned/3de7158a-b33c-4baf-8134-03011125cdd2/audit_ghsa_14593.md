# [H] dio vulnerable to CRLF injection with HTTP method string

## Summary
Severity: High
Advisory: GHSA-9324-jv53-9cc8
CVE: CVE-2021-31402
CWE: CWE-93
Ecosystem: Pub
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-21
Source: https://github.com/advisories/GHSA-9324-jv53-9cc8
Type: github-advisory

## Affected
- Pub: `dio` — affected >=0 <5.0.0

## Details
### Impact
The dio package 4.0.0 for Dart allows CRLF injection if the attacker controls the HTTP method string, a different vulnerability than CVE-2020-35669.

### Patches
The vulnerability has been resolved by https://github.com/cfug/dio/commit/927f79e93ba39f3c3a12c190624a55653d577984, and included since v5.0.0.

### Workarounds
Cherry-pick the commit to your own fork can resolves the vulberability too.

### References
- https://nvd.nist.gov/vuln/detail/CVE-2021-31402
- https://osv.dev/GHSA-jwpw-q68h-r678
- https://github.com/cfug/dio/issues/1130
- https://github.com/cfug/dio/issues/1752

## References
- https://github.com/cfug/dio/security/advisories/GHSA-9324-jv53-9cc8
- https://nvd.nist.gov/vuln/detail/CVE-2021-31402
- https://github.com/cfug/dio/issues/1752
- https://github.com/flutterchina/dio/issues/1130
- https://github.com/cfug/dio/commit/927f79e93ba39f3c3a12c190624a55653d577984
- https://github.com/cfug/dio
- https://osv.dev/GHSA-jwpw-q68h-r678
- https://security.snyk.io/vuln/SNYK-PUB-DIO-5891148
