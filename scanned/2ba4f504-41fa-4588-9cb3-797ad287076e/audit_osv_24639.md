# [H] Local file Inclusion (LFI) in Forum Infusion via Directory Traversal

## Summary
Severity: High
Advisory: CVE-2023-2453
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-09-05
Source: https://osv.dev/vulnerability/CVE-2023-2453
Type: osv

## Details
There is insufficient sanitization of tainted file names that are directly concatenated with a path that is subsequently passed to a ‘require_once’ statement. This allows arbitrary files with the ‘.php’ extension for which the absolute path is known to be included and executed. There are no known means in PHPFusion through which an attacker can upload and target a ‘.php’ file payload.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2453.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2453
- https://www.synopsys.com/blogs/software-security/cyrc-vulnerability-advisory-cve-2023-2453/
- https://github.com/PHPFusion/PHPFusion
