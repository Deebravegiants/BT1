# [C] CVE-2018-25332

## Summary
Severity: Critical
Advisory: CVE-2018-25332
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-05-17
Source: https://osv.dev/vulnerability/CVE-2018-25332
Type: osv

## Details
GitBucket 4.23.1 contains an unauthenticated remote code execution vulnerability that allows attackers to execute arbitrary commands by exploiting weak secret token generation and insecure file upload functionality. Attackers can brute-force the Blowfish encryption key, upload a malicious JAR plugin via the git-lfs endpoint, and execute system commands through an exposed exploit endpoint.

## References
- https://security.szurek.pl/
- https://www.vulncheck.com/advisories/gitbucket-unauthenticated-remote-code-execution
- https://www.exploit-db.com/exploits/44668
- https://github.com/gitbucket/gitbucket
