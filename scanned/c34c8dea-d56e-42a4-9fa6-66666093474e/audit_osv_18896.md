# [C] CVE-2020-36911

## Summary
Severity: Critical
Advisory: CVE-2020-36911
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2020-36911
Type: osv

## Details
Covenant 0.1.3 - 0.5 contains a remote code execution vulnerability that allows attackers to craft malicious JWT tokens with administrative privileges. Attackers can generate forged tokens with admin roles and upload custom DLL payloads to execute arbitrary commands on the target system.

## References
- https://cobbr.io/Covenant.html
- https://github.com/Zeop-CyberSec/covenant_rce/blob/master/covenant_jwt_rce.rb
- https://www.vulncheck.com/advisories/covenant-remote-code-execution-rce
- https://web.archive.org/web/20201013165001/https://twitter.com/cobbr_io/status/1316058367161401344
- https://github.com/cobbr/Covenant
- https://web.archive.org/web/20201101052547/https://blog.null.farm/hunting-the-hunters
- https://www.exploit-db.com/exploits/51141
