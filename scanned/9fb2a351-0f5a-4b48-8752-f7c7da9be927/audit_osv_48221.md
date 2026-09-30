# [H] CVE-2017-2824

## Summary
Severity: High
Advisory: CVE-2017-2824
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-24
Source: https://osv.dev/vulnerability/CVE-2017-2824
Type: osv

## Details
An exploitable code execution vulnerability exists in the trapper command functionality of Zabbix Server 2.4.X. A specially crafted set of packets can cause a command injection resulting in remote code execution. An attacker can make requests from an active Zabbix Proxy to trigger this vulnerability.

## References
- http://www.debian.org/security/2017/dsa-3937
- http://www.securityfocus.com/bid/98083
- https://talosintelligence.com/vulnerability_reports/TALOS-2017-0325
