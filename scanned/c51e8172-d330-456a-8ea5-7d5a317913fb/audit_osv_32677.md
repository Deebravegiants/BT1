# [M] merbanan/rtl_433 <= 25.02 Stack-based Buffer Overflow

## Summary
Severity: Medium
Advisory: CVE-2025-34450
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-18
Source: https://osv.dev/vulnerability/CVE-2025-34450
Type: osv

## Details
merbanan/rtl_433 versions up to and including 25.02 and prior to commit 25e47f8 contain a stack-based buffer overflow vulnerability in the function parse_rfraw() located in src/rfraw.c. When processing crafted or excessively large raw RF input data, the application may write beyond the bounds of a stack buffer, resulting in memory corruption or a crash. This vulnerability can be exploited to cause a denial of service and, under certain conditions, may be leveraged for further exploitation depending on the execution environment and available mitigations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/34xxx/CVE-2025-34450.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-34450
- https://www.vulncheck.com/advisories/merbanan-rtl-433-stack-based-buffer-overflow
- https://github.com/merbanan/rtl_433/issues/3375
- https://github.com/dd32/rtl_433/commit/25e47f8
- https://github.com/merbanan/rtl_433
- https://github.com/marlinkcyber/advisories/blob/main/advisories/MCSAID-2025-004-rtl_433-rfraw-parse-overflow.md
