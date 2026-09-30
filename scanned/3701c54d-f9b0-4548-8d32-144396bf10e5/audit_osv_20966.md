# [M] CVE-2021-39190

## Summary
Severity: Medium
Advisory: CVE-2021-39190
Aliases: GHSA-3324-57w6-jxcq
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-09-22
Source: https://osv.dev/vulnerability/CVE-2021-39190
Type: osv

## Details
The SCCM plugin for GLPI is a plugin to synchronize computers from SCCM (version 1802) to GLPI. In versions prior to 2.3.0, the Configuration page is publicly accessible in read-only mode. This issue is patched in version 2.3.0. No known workarounds exist.

## References
- https://github.com/pluginsGLPI/sccm/security/advisories/GHSA-3324-57w6-jxcq
- https://github.com/pluginsGLPI/sccm/commit/29a7f92d32a0cf9aa3f22c52c50b738274d2813e
