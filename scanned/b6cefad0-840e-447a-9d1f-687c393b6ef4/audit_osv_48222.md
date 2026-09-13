# [H] CVE-2017-2825

## Summary
Severity: High
Advisory: CVE-2017-2825
CVSS: 7.0 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:L)
Published: 2018-04-20
Source: https://osv.dev/vulnerability/CVE-2017-2825
Type: osv

## Details
In the trapper functionality of Zabbix Server 2.4.x, specifically crafted trapper packets can pass database logic checks, resulting in database writes. An attacker can set up a Man-in-the-Middle server to alter trapper requests made between an active Zabbix proxy and Server to trigger this vulnerability.

## References
- https://www.debian.org/security/2017/dsa-3937
- http://www.securityfocus.com/bid/98094
- https://talosintelligence.com/vulnerability_reports/TALOS-2017-0326
