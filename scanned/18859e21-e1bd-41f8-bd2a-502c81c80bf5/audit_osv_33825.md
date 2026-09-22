# [C] CVE-2025-50972

## Summary
Severity: Critical
Advisory: CVE-2025-50972
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-27
Source: https://osv.dev/vulnerability/CVE-2025-50972
Type: osv

## Details
SQL Injection vulnerability in AbanteCart 1.4.2, allows unauthenticated attackers to execute arbitrary SQL commands via the tmpl_id parameter to index.php. Three techniques have been demonstrated: error-based injection using a crafted FLOOR-based payload, time-based blind injection via SLEEP(), and UNION-based injection to extract arbitrary data.

## References
- https://github.com/4rdr/proofs/blob/main/info/abantecart_sql_injection_1.4.2_via_template_parameter.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/50xxx/CVE-2025-50972.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-50972
