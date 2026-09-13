# [H] CVE-2025-29487

## Summary
Severity: High
Advisory: CVE-2025-29487
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2025-29487
Type: osv

## Details
An out-of-memory error in the parseABC_STRING_INFO function of libming v0.4.8 allows attackers to cause a Denial of Service (DoS) due to allocator exhaustion.

## References
- https://github.com/goodmow/PoC/blob/main/libming/libming-fuzz6.readme
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/29xxx/CVE-2025-29487.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-29487
- https://github.com/libming/libming/issues/330
