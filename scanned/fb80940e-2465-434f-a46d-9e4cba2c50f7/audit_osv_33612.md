# [H] Apache ORC: Potential Heap Buffer Overflow during C++ LZO Decompression

## Summary
Severity: High
Advisory: CVE-2025-47436
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:P/PR:H/UI:A/VC:L/VI:H/VA:H/SC:L/SI:H/SA:H/S:N/RE:M/U:Amber)
Published: 2025-05-14
Source: https://osv.dev/vulnerability/CVE-2025-47436
Type: osv

## Details
Heap-based Buffer Overflow vulnerability in Apache ORC.

A vulnerability has been identified in the ORC C++ LZO decompression logic, where specially crafted malformed ORC files can cause the decompressor to allocate a 250-byte buffer but then attempts to copy 295 bytes into it. It causes memory corruption.

This issue affects Apache ORC C++ library: through 1.8.8, from 1.9.0 through 1.9.5, from 2.0.0 through 2.0.4, from 2.1.0 through 2.1.1.

Users are recommended to upgrade to version 1.8.9, 1.9.6, 2.0.5, and 2.1.2, which fix the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/05/13/4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/47xxx/CVE-2025-47436.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-47436
- https://orc.apache.org/security/CVE-2025-47436/
- https://lists.apache.org/thread/kd6tlv8fs5jybmsgxr4vrkdxyc866wrn
