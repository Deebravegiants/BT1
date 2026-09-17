# [H] Azure RTOS NetX Duo Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2023-48315
Aliases: GHSA-rj6h-jjg2-7gf3
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-12-05
Source: https://osv.dev/vulnerability/CVE-2023-48315
Type: osv

## Details
Azure RTOS NetX Duo is a TCP/IP network stack designed specifically for deeply embedded real-time and IoT applications. An attacker can cause remote code execution due to memory overflow vulnerabilities in Azure RTOS NETX Duo. The affected components include processes/functions related to ftp and sntp in RTOS v6.2.1 and below. The fixes have been included in NetX Duo release 6.3.0. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/48xxx/CVE-2023-48315.json
- https://github.com/azure-rtos/netxduo/security/advisories/GHSA-rj6h-jjg2-7gf3
- https://nvd.nist.gov/vuln/detail/CVE-2023-48315
