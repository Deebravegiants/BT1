# [C] CVE-2021-47736

## Summary
Severity: Critical
Advisory: CVE-2021-47736
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2025-12-23
Source: https://osv.dev/vulnerability/CVE-2021-47736
Type: osv

## Details
CMSimple_XH 1.7.4 contains an authenticated remote code execution vulnerability in the content editing functionality that allows administrative users to upload malicious PHP files. Attackers with valid credentials can exploit the CSRF token mechanism to create a PHP shell file that enables arbitrary command execution on the server.

## References
- https://www.cmsimple-xh.org/
- https://www.vulncheck.com/advisories/cmsimplexh-authenticated-remote-code-execution-via-content-editing
- https://www.exploit-db.com/exploits/50367
