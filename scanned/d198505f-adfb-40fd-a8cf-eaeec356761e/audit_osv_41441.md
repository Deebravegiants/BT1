# [H] CVE-2026-6067

## Summary
Severity: High
Advisory: CVE-2026-6067
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-6067
Type: osv

## Details
A heap buffer overflow vulnerability exists in the Netwide Assembler (NASM) due to a lack of bounds checking in the obj_directive() function. This vulnerability can be exploited by a user assembling a malicious .asm file, potentially leading to heap memory corruption, denial of service (crash), and arbitrary code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6067.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-6067
- https://github.com/netwide-assembler/nasm/issues/203
