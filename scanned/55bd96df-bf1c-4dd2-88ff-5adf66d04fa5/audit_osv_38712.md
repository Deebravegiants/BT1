# [H] KeePassXC OpenSSL Configuration Uncontrolled Search Path Element Local Privilege Escalation Vulnerability

## Summary
Severity: High
Advisory: CVE-2026-4158
Aliases: GHSA-4gr2-cr97-q9fx
CVSS: 7.3 (CVSS:3.0/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-11
Source: https://osv.dev/vulnerability/CVE-2026-4158
Type: osv

## Details
KeePassXC OpenSSL Configuration Uncontrolled Search Path Element Local Privilege Escalation Vulnerability. This vulnerability allows local attackers to escalate privileges on affected installations of KeePassXC. An attacker must first obtain the ability to execute low-privileged code on the target system in order to exploit this vulnerability.

The specific flaw exists within the configuration of OpenSSL. The product loads configuration from an unsecured location. An attacker can leverage this vulnerability to escalate privileges and execute arbitrary code in the context of KeePassXC when run by a target user on the system. Was ZDI-CAN-29156.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/4xxx/CVE-2026-4158.json
- https://github.com/keepassxreboot/keepassxc/security/advisories/GHSA-4gr2-cr97-q9fx
- https://nvd.nist.gov/vuln/detail/CVE-2026-4158
- https://www.zerodayinitiative.com/advisories/ZDI-26-215/
