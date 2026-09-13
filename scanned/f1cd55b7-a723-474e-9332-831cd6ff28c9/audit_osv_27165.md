# [H] Radare2: command injection via pebble application files in radare2

## Summary
Severity: High
Advisory: CVE-2024-11858
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2024-12-15
Source: https://osv.dev/vulnerability/CVE-2024-11858
Type: osv

## Details
A flaw was found in Radare2, which contains a command injection vulnerability caused by insufficient input validation when handling Pebble Application files. Maliciously crafted inputs can inject shell commands during command parsing, leading to unintended behavior during file processing​

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/11xxx/CVE-2024-11858.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-11858
- https://bugzilla.redhat.com/show_bug.cgi?id=2329102
- https://github.com/radareorg/radare2
