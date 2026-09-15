# [H] LibreNMS Virtualisation Discovery Module RCE

## Summary
Severity: High
Advisory: CVE-2026-80214
Aliases: GHSA-7hmq-j399-mqwf
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80214
Type: osv

## Details
LibreNMS’s Virtualization Discovery module is vulnerable to command line injection. An authenticated admin user can execute arbitrary code on the host server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80214.json
- https://github.com/librenms/librenms/security/advisories/GHSA-7hmq-j399-mqwf
- https://nvd.nist.gov/vuln/detail/CVE-2026-80214
- https://projectblack.io/blog/librenms-authenticated-rce-26-5-0/#rce-by-command-line-injection-2641
