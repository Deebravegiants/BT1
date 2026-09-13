# [H] CVE-2025-45331

## Summary
Severity: High
Advisory: CVE-2025-45331
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-06-20
Source: https://osv.dev/vulnerability/CVE-2025-45331
Type: osv

## Details
brplot v420.69.1 contains a Null Pointer Dereference (NPD) vulnerability in the br_dagens_handle_once function of its data processing module, leading to unpredictable program behavior, causing segmentation faults, and program crashes.

## References
- https://gist.github.com/QiuYitai/9dd6db6e9dfc03868b9c886b801502ac
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/45xxx/CVE-2025-45331.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-45331
- https://github.com/branc116/brplot/commit/b90e93a0e0d514d48f38d1584496130fa5fe4fe4
