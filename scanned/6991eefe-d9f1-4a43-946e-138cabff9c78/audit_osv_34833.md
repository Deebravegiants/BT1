# [C] CVE-2025-65570

## Summary
Severity: Critical
Advisory: CVE-2025-65570
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-29
Source: https://osv.dev/vulnerability/CVE-2025-65570
Type: osv

## Details
A type confusion in jsish 2.0 allows incorrect control flow during execution of the OP_NEXT opcode. When an “instanceof” expression uses an array element access as the left-hand operand inside a for-in loop, the instructions implementation leaves an additional array reference on the stack rather than consuming it during OP_INSTANCEOF. As a result, OP_NEXT interprets the array as an iterator object and reads the iterCmd function pointer from an invalid structure, potentially causing a crash or enabling code execution depending on heap layout.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65570.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65570
- https://blog.mcsky.ro/writeups/2025/11/15/inline8-writeup.html
