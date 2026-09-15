# [C] CVE-2020-37167

## Summary
Severity: Critical
Advisory: CVE-2020-37167
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-02-12
Source: https://osv.dev/vulnerability/CVE-2020-37167
Type: osv

## Details
ClamAV versions prior to 0.103.0-rc contain a vulnerability in function name processing through the ClamBC bytecode interpreter that allows attackers to manipulate bytecode function names. Attackers can exploit the weak input validation in function name encoding to potentially execute malicious bytecode or cause unexpected behavior in the ClamAV engine.

## References
- https://www.clamav.net/
- https://www.exploit-db.com/exploits/47687
- https://www.vulncheck.com/advisories/clamav-clambc-clambc-executable-regular-expression-error
- https://github.com/Cisco-Talos/clamav/commit/cd2f2975b93277de7f74464d48adb378375a305f
