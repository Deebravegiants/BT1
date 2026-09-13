# [H] CVE-2025-48732

## Summary
Severity: High
Advisory: CVE-2025-48732
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-07-24
Source: https://osv.dev/vulnerability/CVE-2025-48732
Type: osv

## Details
An incomplete blacklist exists in the .htaccess sample of WWBN AVideo 14.4 and dev master commit 8a8954ff. A specially crafted HTTP request can lead to a arbitrary code execution. An attacker can request a .phar file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2025-2213
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2025-2213
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48732.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-48732
