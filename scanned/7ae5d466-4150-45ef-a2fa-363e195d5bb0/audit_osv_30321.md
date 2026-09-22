# [M] CVE-2024-50596

## Summary
Severity: Medium
Advisory: CVE-2024-50596
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-04-02
Source: https://osv.dev/vulnerability/CVE-2024-50596
Type: osv

## Details
An integer underflow vulnerability exists in the HTTP server PUT request functionality of STMicroelectronics X-CUBE-AZRTOS-WL 2.0.0. A specially crafted network packet can lead to denial of service. An attacker can send a malicious packet to trigger this vulnerability.This vulnerability affects the NetX Duo Web Component HTTP Server implementation which can be found in x-cube-azrtos-f7\Middlewares\ST\netxduo\addons\web\nx_web_http_server.c

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2024-2103
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2024-2103
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50596.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50596
