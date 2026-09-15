# [M] CVE-2025-62813

## Summary
Severity: Medium
Advisory: CVE-2025-62813
CVSS: 5.9 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2025-10-23
Source: https://osv.dev/vulnerability/CVE-2025-62813
Type: osv

## Details
LZ4 through 1.10.0 allows attackers to cause a denial of service (application crash) or possibly have unspecified other impact when the application processes untrusted LZ4 frames. For example, LZ4F_createCDict_advanced in lib/lz4frame.c mishandles NULL checks.

## References
- https://github.com/lz4/lz4/commit/f64efec011c058bd70348576438abac222fe6c82
- https://github.com/lz4/lz4/pull/1593
