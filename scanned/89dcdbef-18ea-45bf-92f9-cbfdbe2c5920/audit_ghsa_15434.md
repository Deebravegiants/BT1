# [M] Serilog Client IP Spoofing vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5x5q-cqf6-gj8r
CVE: CVE-2024-44930
CWE: CWE-348, CWE-79
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-29
Source: https://github.com/advisories/GHSA-5x5q-cqf6-gj8r
Type: github-advisory

## Affected
- NuGet: `Serilog.Enrichers.ClientInfo` — affected >=0 <2.1.0

## Details
Serilog (before v2.1.0) contains a Client IP Spoofing vulnerability, which allows attackers to falsify their IP addresses in log files by specifying an arbitrary IP as a value of X-Forwarded-For or Client-Ip headers while performing HTTP requests.

It is not possible to configure Serilog.Enrichers.ClientInfo to not trust the X-Forwarded-For header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-44930
- https://github.com/serilog-contrib/serilog-enrichers-clientinfo/issues/29
- https://github.com/serilog-contrib/serilog-enrichers-clientinfo/pull/38
- https://github.com/serilog-contrib/serilog-enrichers-clientinfo/commit/a72051d1900131e6fb30bcfd9491a988167fb6ac
- https://github.com/serilog-contrib/serilog-enrichers-clientinfo
- https://github.com/serilog-contrib/serilog-enrichers-clientinfo/releases/tag/v2.1.0
