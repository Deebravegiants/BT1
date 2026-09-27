# [M] CVE-2026-6068

## Summary
Severity: Medium
Advisory: CVE-2026-6068
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-6068
Type: osv

## Details
NASM contains a heap use after free vulnerability in response file (-@) processing where a dangling pointer to freed memory is stored in the global depend_file and later dereferenced, as the response-file buffer is freed before the pointer is used, allowing for data corruption or remote code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6068.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-6068
- https://github.com/netwide-assembler/nasm/issues/222
- https://sekai.team/blog/nasm-cve-disclosure/cve-2026-6068
