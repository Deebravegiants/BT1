# [M] CVE-2021-47942

## Summary
Severity: Medium
Advisory: CVE-2021-47942
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-05-16
Source: https://osv.dev/vulnerability/CVE-2021-47942
Type: osv

## Details
Home Assistant Community Store (HACS) prior to 1.10.0 contains a path traversal vulnerability that allows unauthenticated attackers to read sensitive files by traversing directories via the /hacsfiles/ endpoint. Attackers can retrieve the .storage/auth file containing user credentials and refresh tokens, then craft valid JWT tokens to gain administrative access to Home Assistant instances.

## References
- https://www.home-assistant.io/
- https://www.vulncheck.com/advisories/home-assistant-community-store-path-traversal-account-takeover
- https://github.com/hacs/integration
- https://www.exploit-db.com/exploits/49495
