# [H] CVE-2018-3885

## Summary
Severity: High
Advisory: CVE-2018-3885
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-12
Source: https://osv.dev/vulnerability/CVE-2018-3885
Type: osv

## Details
An exploitable SQL injection vulnerability exists in the authenticated part of ERPNext v10.1.6. Specially crafted web requests can cause SQL injections resulting in data compromise. The order_by parameter can be used to perform an SQL injection attack. An attacker can use a browser to trigger these vulnerabilities, and no special tools are required.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2018-0560
