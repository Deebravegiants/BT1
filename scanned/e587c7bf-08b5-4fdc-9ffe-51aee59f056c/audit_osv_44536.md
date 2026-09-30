# [C] LibreNMS 23.10.0 before 26.4.0 OS Command Injection via Hostname

## Summary
Severity: Critical
Advisory: CVE-2026-84194
Aliases: GHSA-wff2-9gjr-95f3
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-84194
Type: osv

## Details
LibreNMS versions >= 23.10.0 and < 26.2.0 (fixed in 26.4.0) contain an authenticated OS command injection vulnerability in libvirt discovery. When libvirt support is enabled (enable_libvirt=true), the device hostname ($this->getDevice()->hostname) is concatenated into shell commands (ssh, virsh list/dumpxml/domstate) in VminfoLibvirt.php and passed to exec() without escapeshellarg() or argument separation. An authenticated admin can set a crafted device hostname to inject arbitrary OS commands, leading to remote code execution in the discovery worker context.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84194.json
- https://github.com/librenms/librenms/security/advisories/GHSA-wff2-9gjr-95f3
- https://nvd.nist.gov/vuln/detail/CVE-2026-84194
- https://www.vulncheck.com/advisories/librenms-23.10.0-before-26.4.0-os-command-injection-via-hostname
