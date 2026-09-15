# [M] CVE-2024-50385

## Summary
Severity: Medium
Advisory: CVE-2024-50385
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-02
Source: https://osv.dev/vulnerability/CVE-2024-50385
Type: osv

## Details
A denial of service vulnerability exists in the NetX Component HTTP server functionality of STMicroelectronics X-CUBE-AZRTOS-WL 2.0.0. A specially crafted network packet can lead to denial of service. An attacker can send a malicious packet to trigger this vulnerability.This vulnerability affects X-CUBE-AZRTOS-F7 NetX Duo Component HTTP Server HTTP server v 1.1.0. This HTTP server implementation is contained in this file - x-cube-azrtos-f7\Middlewares\ST\netxduo\addons\http\nxd_http_server.c

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2024-2097
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2024-2097
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50385.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50385
