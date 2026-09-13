# [C] CVE-2024-41617

## Summary
Severity: Critical
Advisory: CVE-2024-41617
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-24
Source: https://osv.dev/vulnerability/CVE-2024-41617
Type: osv

## Details
Money Manager EX WebApp (web-money-manager-ex) 1.2.2 is vulnerable to Incorrect Access Control. The `redirect_if_not_loggedin` function in `functions_security.php` fails to terminate script execution after redirecting unauthenticated users. This flaw allows an unauthenticated attacker to upload arbitrary files, potentially leading to Remote Code Execution.

## References
- https://github.com/moneymanagerex/web-money-manager-ex/releases/tag/v1.2.3
- https://youtu.be/JaOrlT9G3yo?t=88
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41617.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41617
- https://github.com/moneymanagerex/web-money-manager-ex/issues/51
- https://github.com/moneymanagerex/web-money-manager-ex/commit/f2850b295ee21bc299799343a3bc4d004d05651d
