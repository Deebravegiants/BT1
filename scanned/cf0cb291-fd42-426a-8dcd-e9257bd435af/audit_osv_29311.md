# [C] CVE-2024-41618

## Summary
Severity: Critical
Advisory: CVE-2024-41618
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-24
Source: https://osv.dev/vulnerability/CVE-2024-41618
Type: osv

## Details
Money Manager EX WebApp (web-money-manager-ex) 1.2.2 is vulnerable to SQL Injection in the `transaction_delete_group` function. The vulnerability is due to improper sanitization of user input in the `TrDeleteArr` parameter, which is directly incorporated into an SQL query.

## References
- https://github.com/moneymanagerex/web-money-manager-ex/releases/tag/v1.2.3
- https://www.youtube.com/watch?v=JaOrlT9G3yo
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41618.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41618
- https://github.com/moneymanagerex/web-money-manager-ex/issues/51
- https://github.com/moneymanagerex/web-money-manager-ex/commit/f2850b295ee21bc299799343a3bc4d004d05651d
