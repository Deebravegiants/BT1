# [C] Authenticated amportal search for ‘freepbx_engine’ in non root writeable directories leads to potential privilege escalation

## Summary
Severity: Critical
Advisory: CVE-2025-67722
Aliases: GHSA-p42w-v77m-hfp8
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-67722
Type: osv

## Details
FreePBX is an open-source web-based graphical user interface (GUI) that manages Asterisk. Prior to versions 16.0.45 and 17.0.24 of the FreePBX framework, an authenticated local privilege escalation exists in the deprecated FreePBX startup script `amportal`. In the deprecated `amportal` utility, the lookup for the `freepbx_engine` file occurs in `/etc/asterisk/` directories. Typically, these are configured by FreePBX as writable by the **asterisk** user and any members of the **asterisk** group. This means that a member of the **asterisk** group can add their own `freepbx_engine` file in `/etc/asterisk/` and upon `amportal` executing, it would exec that file with root permissions (even though the file was created and placed by a non-root user). Version 16.0.45 and 17.0.24 contain a fix for the issue. Other mitigation strategies are also available. Confirm only trusted local OS system users are members of the `asterisk` group. Look for suspicious files in the `/etc/asterisk/` directory (via Admin -> Config Edit in the GUI, or via CLI). Double-check that `live_dangerously = no` is set (or unconfigured, as the default is **no**) in `/etc/asterisk/asterisk.conf` file. Eliminate any unsafe custom use of Asterisk dial plan applications and functions that potentially can manipulate the file system, e.g., System(), FILE(), etc.

## References
- https://www.freepbx.org/watch-what-we-do-with-security-fixes-%f0%9f%91%80
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67722.json
- https://github.com/FreePBX/security-reporting/security/advisories/GHSA-p42w-v77m-hfp8
- https://nvd.nist.gov/vuln/detail/CVE-2025-67722
