# [H] SQL Injection vulnerability when managing SNMP Notification Receivers

## Summary
Severity: High
Advisory: CVE-2023-51448
Aliases: GHSA-w85f-7c4w-7594
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-12-22
Source: https://osv.dev/vulnerability/CVE-2023-51448
Type: osv

## Details
Cacti provides an operational monitoring and fault management framework. Version 1.2.25 has a Blind SQL Injection (SQLi) vulnerability within the SNMP Notification Receivers feature in the file `‘managers.php’`. An authenticated attacker with the “Settings/Utilities” permission can send a crafted HTTP GET request to the endpoint `‘/cacti/managers.php’` with an SQLi payload in the `‘selected_graphs_array’` HTTP GET parameter. As of time of publication, no patched versions exist.

## References
- https://github.com/Cacti/cacti/blob/5f6f65c215d663a775950b2d9db35edbaf07d680/managers.php#L941
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RBEOAFKRARQHTDIYSL723XAFJ2Q6624X/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/51xxx/CVE-2023-51448.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-w85f-7c4w-7594
- https://nvd.nist.gov/vuln/detail/CVE-2023-51448
