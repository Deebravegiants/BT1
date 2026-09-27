# [M] hashcat KeePass KDBX v4 Module Heap Buffer Overflow via Token Field

## Summary
Severity: Medium
Advisory: CVE-2026-68765
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:H/UI:A/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-68765
Type: osv

## Details
hashcat master branch builds after v7.1.2 contain a heap buffer overflow vulnerability in the KeePass AESKDF/KDBX v4 module (module 34301) that allows attackers to corrupt adjacent heap memory by supplying an oversized ninth hash field token. The module accepts up to 600 hex characters for the ninth token field but decodes it into a fixed 256-byte buffer with no length check, allowing a maximal input to write up to 44 bytes past the buffer boundary into adjacent esalt fields and heap chunk metadata, potentially enabling heap corruption or memory access violations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68765.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68765
- https://www.vulncheck.com/advisories/hashcat-keepass-kdbx-v4-module-heap-buffer-overflow-via-token-field
- https://github.com/hashcat/hashcat/pull/4755
- https://github.com/hashcat/hashcat
- https://github.com/hashcat/hashcat/commit/6f374c4ff7d5dc951530fbbbcf6b45e3c169b100
