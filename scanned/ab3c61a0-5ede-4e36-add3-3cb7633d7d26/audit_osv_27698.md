# [H] CVE-2024-25003

## Summary
Severity: High
Advisory: CVE-2024-25003
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-09
Source: https://osv.dev/vulnerability/CVE-2024-25003
Type: osv

## Details
KiTTY versions 0.76.1.13 and before is vulnerable to a stack-based buffer overflow via the hostname, occurs due to insufficient bounds checking and input sanitization. This allows an attacker to overwrite adjacent memory, which leads to arbitrary code execution.

## References
- http://packetstormsecurity.com/files/177031/KiTTY-0.76.1.13-Command-Injection.html
- http://packetstormsecurity.com/files/177032/KiTTY-0.76.1.13-Buffer-Overflows.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25003.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25003
- http://seclists.org/fulldisclosure/2024/Feb/13
- http://seclists.org/fulldisclosure/2024/Feb/14
- https://blog.defcesco.io/CVE-2024-25003-CVE-2024-25004
