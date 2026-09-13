# [H] Low privilege user is able to exploit the service and gain SYSTEM privileges in UltraVNC server

## Summary
Severity: High
Advisory: CVE-2022-24750
Aliases: GHSA-3mvp-cp5x-vj5g
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-03-10
Source: https://osv.dev/vulnerability/CVE-2022-24750
Type: osv

## Details
UltraVNC is a free and open source remote pc access software. A vulnerability has been found in versions prior to 1.3.8.0 in which the DSM plugin module, which allows a local authenticated user to achieve local privilege escalation (LPE) on a vulnerable system. The vulnerability has been fixed to allow loading of plugins from the installed directory. Affected users should upgrade their UltraVNC to 1.3.8.1. Users unable to upgrade should not install and run UltraVNC server as a service. It is advisable to create a scheduled task on a low privilege account to launch WinVNC.exe instead. There are no known workarounds if winvnc needs to be started as a service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24750.json
- https://github.com/ultravnc/UltraVNC/security/advisories/GHSA-3mvp-cp5x-vj5g
- https://nvd.nist.gov/vuln/detail/CVE-2022-24750
- https://github.com/ultravnc/UltraVNC/commit/36a31b37b98f70c1db0428f5ad83170d604fb352
- https://github.com/bowtiejicode/UltraVNC-DSMPlugin-LPE
