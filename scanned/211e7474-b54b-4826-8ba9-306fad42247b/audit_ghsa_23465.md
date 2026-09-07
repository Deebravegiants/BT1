# [C] Apache NiFi XSS issue in context path handling

## Summary
Severity: Critical
Advisory: GHSA-29ph-fjf3-c5cm
CVE: CVE-2017-15697
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-29ph-fjf3-c5cm
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi` — affected >=1.0.0 <1.5.0

## Details
A malicious `X-ProxyContextPath` or `X-Forwarded-Context` header containing external resources or embedded code could cause remote code execution. The fix to properly handle these headers was applied on the Apache NiFi 1.5.0 release. Users running a prior 1.x release should upgrade to the appropriate release.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15697
- https://nifi.apache.org/security.html#CVE-2017-15697
