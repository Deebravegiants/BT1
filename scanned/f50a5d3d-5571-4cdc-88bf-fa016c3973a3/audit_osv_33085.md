# [M] Buffer overflow in Si91x crypto APIs

## Summary
Severity: Medium
Advisory: CVE-2025-3873
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-3873
Type: osv

## Details
The following APIs for the Silcon Labs SiWx91x prior to vesion 3.4.0 failed to check the size of the output buffer of the caller which could lead to data corruption on the host (Cortex-M4) application.


sl_si91x_aes
sl_si91x_gcm
sl_si91x_ccm 
sl_si91x_sha

## References
- https://docs.silabs.com/wiseconnect/latest/sisdk-wifi-release-notes/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/3xxx/CVE-2025-3873.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-3873
- https://community.silabs.com/068Vm00000SSlOu
- https://github.com/SiliconLabs/wiseconnect
