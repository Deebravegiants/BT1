# [M] CVE-2019-7616

## Summary
Severity: Medium
Advisory: CVE-2019-7616
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-07-30
Source: https://osv.dev/vulnerability/CVE-2019-7616
Type: osv

## Details
Kibana versions before 6.8.2 and 7.2.1 contain a server side request forgery (SSRF) flaw in the graphite integration for Timelion visualizer. An attacker with administrative Kibana access could set the timelion:graphite.url configuration option to an arbitrary URL. This could possibly lead to an attacker accessing external URL resources as the Kibana process on the host system.

## References
- https://www.elastic.co/community/security/
