# [C] Second Stage Gecko Bootloader GBL Parser Buffer Overrun Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2023-4041
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-08-23
Source: https://osv.dev/vulnerability/CVE-2023-4041
Type: osv

## Details
Buffer Copy without Checking Size of Input ('Classic Buffer Overflow'), Out-of-bounds Write, Download of Code Without Integrity Check vulnerability in Silicon Labs Gecko Bootloader on ARM (Firmware Update File Parser modules) allows Code Injection, Authentication Bypass.This issue affects "Standalone" and "Application" versions of Gecko Bootloader.

## References
- https://siliconlabs.lightning.force.com/sfc/servlet.shepherd/document/download/0698Y00000XT8GsQAL?operationContext=S1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4041.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4041
- https://github.com/SiliconLabs/gecko_sdk/releases
