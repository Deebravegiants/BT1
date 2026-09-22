# [C] FreePBX Administration GUI is Vulnerable to Authenticated Command Injection

## Summary
Severity: Critical
Advisory: CVE-2025-64328
Aliases: GHSA-vm9p-46mv-5xvw
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-11-07
Source: https://osv.dev/vulnerability/CVE-2025-64328
Type: osv

## Details
FreePBX Endpoint Manager is a module for managing telephony endpoints in FreePBX systems. In versions 17.0.2.36 and above before 17.0.3, the filestore module within the Administrative interface is vulnerable to a post-authentication command injection by an authenticated known user via the testconnection -> check_ssh_connect() function. An attacker can leverage this vulnerability to obtain remote access to the system as an asterisk user. This issue is fixed in version 17.0.3.

## References
- https://github.com/FreePBX/filestore/blob/f0e3983059271efd80b483ec823310ef19a59013/drivers/SSH/testconnection.php#L2
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-64328
- https://www.freepbx.org/watch-what-we-do-with-security-fixes-%f0%9f%91%80
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64328.json
- https://github.com/FreePBX/security-reporting/security/advisories/GHSA-vm9p-46mv-5xvw
- https://nvd.nist.gov/vuln/detail/CVE-2025-64328
- https://www.fortinet.com/blog/threat-research/unveiling-the-weaponized-web-shell-encystphp
