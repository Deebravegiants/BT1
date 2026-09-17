# [M] RustDesk Client for Windows Transfer File Link Following Information Disclosure Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2026-2490
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-20
Source: https://osv.dev/vulnerability/CVE-2026-2490
Type: osv

## Details
RustDesk Client for Windows Transfer File Link Following Information Disclosure Vulnerability. This vulnerability allows local attackers to disclose sensitive information on affected installations of RustDesk Client for Windows. An attacker must first obtain the ability to execute low-privileged code on the target system in order to exploit this vulnerability.

The specific flaw exists within the Transfer File feature. By uploading a symbolic link, an attacker can abuse the service to read arbitrary files. An attacker can leverage this vulnerability to disclose information in the context of SYSTEM. Was ZDI-CAN-27909.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/2xxx/CVE-2026-2490.json
- https://github.com/rustdesk/rustdesk/pull/13736
- https://nvd.nist.gov/vuln/detail/CVE-2026-2490
- https://www.zerodayinitiative.com/advisories/ZDI-26-117/
