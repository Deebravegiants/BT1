# [M] Key duplication in GSDK

## Summary
Severity: Medium
Advisory: CVE-2023-32100
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-05-18
Source: https://osv.dev/vulnerability/CVE-2023-32100
Type: osv

## Details
Compiler removal of buffer clearing in 

sli_se_driver_mac_compute

in Silicon Labs Gecko Platform SDK v4.2.1 and earlier results in key material duplication to RAM.

## References
- https://community.silabs.com/sfc/servlet.shepherd/document/download/0698Y00000U19lGQAR?operationContext=S1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32100.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-32100
- https://github.com/SiliconLabs/gecko_sdk
