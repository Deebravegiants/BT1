# [C] Eclipse ThreadX FileX RAM disk driver buffer overflow

## Summary
Severity: Critical
Advisory: CVE-2025-55089
Aliases: GHSA-467v-6j75-3j7g
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-10-16
Source: https://osv.dev/vulnerability/CVE-2025-55089
Type: osv

## Details
In FileX before 6.4.2, the file support module for Eclipse Foundation ThreadX, there was a possible buffer overflow in the FileX RAM disk driver. It could cause a remote execurtion after receiving a crafted sequence of packets

## References
- https://github.com/eclipse-threadx/filex/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55089.json
- https://github.com/eclipse-threadx/filex/security/advisories/GHSA-467v-6j75-3j7g
- https://nvd.nist.gov/vuln/detail/CVE-2025-55089
