# [C] CVE-2019-5151

## Summary
Severity: Critical
Advisory: CVE-2019-5151
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-31
Source: https://osv.dev/vulnerability/CVE-2019-5151
Type: osv

## Details
An exploitable SQL injection vulnerability exist in YouPHPTube 7.7. A specially crafted unauthenticated HTTP request can cause a SQL injection, possibly leading to denial of service, exfiltration of the database and local file inclusion, which could potentially further lead to code execution. An attacker can send an HTTP request to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2019-0941
