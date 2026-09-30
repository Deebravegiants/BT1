# [H] Velocidex WinPmem Out of Bounds Write Vulnerability

## Summary
Severity: High
Advisory: CVE-2024-12668
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-12-16
Source: https://osv.dev/vulnerability/CVE-2024-12668
Type: osv

## Details
Velocidex WinPmem versions below 4.1 suffer from an Out of Bounds Write vulnerability. By using an IO Control, a user space program can trick the driver into writing a 0 into any chosen memory location. In conjunction with information leakage from the WinPmem driver, attackers can discover the location in memory for the  g_CiOptions global symbol. This can be leveraged to disable signed driver enforcement on the target system - allowing attackers to load unsigned drivers.

## References
- https://github.com/Velocidex/WinPmem/releases/tag/v4.1.dev1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12668.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12668
