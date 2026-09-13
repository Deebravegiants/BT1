# [M] Resource exhaustion via Stack overflow in libjxl

## Summary
Severity: Medium
Advisory: CVE-2024-11498
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H)
Published: 2024-11-25
Source: https://osv.dev/vulnerability/CVE-2024-11498
Type: osv

## Details
There exists a stack buffer overflow in libjxl. A specifically-crafted file can cause the JPEG XL decoder to use large amounts of stack space (up to 256mb is possible, maybe 512mb), potentially exhausting the stack. An attacker can craft a file that will cause excessive memory usage. We recommend upgrading past commit 65fbec56bc578b6b6ee02a527be70787bbd053b0.

## References
- https://github.com/libjxl/libjxl/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/11xxx/CVE-2024-11498.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-11498
- https://github.com/libjxl/libjxl/pull/3943
