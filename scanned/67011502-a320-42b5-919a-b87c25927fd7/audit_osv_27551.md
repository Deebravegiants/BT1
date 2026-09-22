# [H] CVE-2024-23749

## Summary
Severity: High
Advisory: CVE-2024-23749
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-09
Source: https://osv.dev/vulnerability/CVE-2024-23749
Type: osv

## Details
KiTTY versions 0.76.1.13 and before is vulnerable to command injection via the filename variable, occurs due to insufficient input sanitization and validation, failure to escape special characters, and insecure system calls (at lines 2369-2390). This allows an attacker to add inputs inside the filename variable, leading to arbitrary code execution.

## References
- http://packetstormsecurity.com/files/177031/KiTTY-0.76.1.13-Command-Injection.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23749.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-23749
- http://seclists.org/fulldisclosure/2024/Feb/13
- http://seclists.org/fulldisclosure/2024/Feb/14
- https://blog.defcesco.io/CVE-2024-23749
