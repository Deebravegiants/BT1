# [C] CVE-2026-33590

## Summary
Severity: Critical
Advisory: CVE-2026-33590
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:P/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-33590
Type: osv

## Details
Insecure default settings of Portainer CE grant regular (non-admin) users privileges that allow host filesystem access and host-level code execution. An authenticated non-administrative user with endpoint access can exploit these settings to read host files or obtain root equivalent 

access on the host.

## References
- http://www.openwall.com/lists/oss-security/2026/06/12/2
- https://github.com/portainer/portainer/commit/3e2fdb1891e81a8e4c5c8beb60e45f07c8ecae52
- https://github.com/portainer/portainer/commit/ac8fa7672e732b44b970c9eaf928eddd2c68796c
- https://intwave.com/blog/2026/02/26/improving-portainer-security.html
