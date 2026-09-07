# [H] Apache NiFi host header poisoning issue

## Summary
Severity: High
Advisory: GHSA-w4x6-j349-9r57
CVE: CVE-2017-12632
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-w4x6-j349-9r57
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi` — affected >=1.0.0 <1.5.0

## Details
A malicious host header in an incoming HTTP request could cause NiFi to load resources from an external server. The fix to sanitize host headers and compare to a controlled whitelist was applied on the Apache NiFi 1.5.0 release. Users running a prior 1.x release should upgrade to the appropriate release.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12632
- https://nifi.apache.org/security.html#CVE-2017-12632
