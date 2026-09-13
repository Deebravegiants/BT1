# [C] BIT-grafana-2022-26148

## Summary
Severity: Critical
Advisory: BIT-grafana-2022-26148
Aliases: CVE-2022-26148
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-grafana-2022-26148
Type: osv

## Affected
- Bitnami: `grafana` — affected >=0 <7.3.5

## Details
An issue was discovered in Grafana through 7.3.4, when integrated with Zabbix. The Zabbix password can be found in the api_jsonrpc.php HTML source code. When the user logs in and allows the user to register, one can right click to view the source code and use Ctrl-F to search for password in api_jsonrpc.php to discover the Zabbix account password and URL address.

## References
- https://2k8.org/post-319.html
- https://security.netapp.com/advisory/ntap-20220425-0005/
- https://nvd.nist.gov/vuln/detail/CVE-2022-26148
