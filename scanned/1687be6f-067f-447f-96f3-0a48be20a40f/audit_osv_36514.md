# [H] EVerest has stack buffer overflow in ifreq.ifr_name when interface name exceeds IFNAMSIZ

## Summary
Severity: High
Advisory: CVE-2026-23995
Aliases: GHSA-p47c-2jpr-mpwx
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-23995
Type: osv

## Details
EVerest is an EV charging software stack. Prior to version 2026.02.0, stack-based buffer overflow in CAN interface initialization: passing an interface name longer than IFNAMSIZ (16) to CAN open routines overflows `ifreq.ifr_name`, corrupting adjacent stack data and enabling potential code execution. A malicious or misconfigured interface name can trigger this before any privilege checks. Version 2026.02.0 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23995.json
- https://github.com/EVerest/EVerest/security/advisories/GHSA-p47c-2jpr-mpwx
- https://nvd.nist.gov/vuln/detail/CVE-2026-23995
