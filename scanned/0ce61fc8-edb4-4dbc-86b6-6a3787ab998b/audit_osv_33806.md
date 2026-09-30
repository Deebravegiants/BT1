# [H] CVE-2025-50360

## Summary
Severity: High
Advisory: CVE-2025-50360
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-03
Source: https://osv.dev/vulnerability/CVE-2025-50360
Type: osv

## Details
A heap buffer overflow in compiler.c and compiler.h in Pepper language 0.1.1commit 961a5d9988c5986d563310275adad3fd181b2bb7. Malicious execution of a pepper source file(.pr) could lead to arbitrary code execution or Denial of Service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/50xxx/CVE-2025-50360.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-50360
- https://github.com/Ch1keen/CVE-2025-50360
- https://github.com/dannyvankooten/pepper-lang
