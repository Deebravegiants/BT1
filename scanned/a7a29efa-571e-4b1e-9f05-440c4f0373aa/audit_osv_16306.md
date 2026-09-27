# [H] CVE-2019-5117

## Summary
Severity: High
Advisory: CVE-2019-5117
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-25
Source: https://osv.dev/vulnerability/CVE-2019-5117
Type: osv

## Details
Exploitable SQL injection vulnerabilities exists in the authenticated portion of YouPHPTube 7.6. Specially crafted web requests can cause SQL injections. An attacker can send a web request with parameters containing SQL injection attacks to trigger this vulnerability, potentially allowing exfiltration of the database, user credentials and in certain configuration, access the underlying operating system.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2019-0908
