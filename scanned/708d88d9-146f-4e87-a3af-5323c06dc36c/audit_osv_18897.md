# [M] CVE-2020-37041

## Summary
Severity: Medium
Advisory: CVE-2020-37041
Aliases: PYSEC-2026-114
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-01-30
Source: https://osv.dev/vulnerability/CVE-2020-37041
Type: osv

## Details
OpenCTI 3.3.1 is vulnerable to a directory traversal attack via the static/css endpoint. An unauthenticated attacker can read arbitrary files from the filesystem by sending crafted GET requests with path traversal sequences (e.g., '../') in the URL. For example, requesting /static/css//../../../../../../../../etc/passwd returns the contents of /etc/passwd. This vulnerability was discovered by Raif Berkay Dincel and confirmed on Linux Mint and Windows 10.

## References
- https://www.opencti.io/
- https://www.vulncheck.com/advisories/opencti-directory-traversal
- https://github.com/OpenCTI-Platform/opencti
- https://www.exploit-db.com/exploits/48595
