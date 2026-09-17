# [H] CVE-2025-29484

## Summary
Severity: High
Advisory: CVE-2025-29484
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2025-29484
Type: osv

## Details
An out-of-memory error in the parseABC_NS_SET_INFO function of libming v0.4.8 allows attackers to cause a Denial of Service (DoS) due to allocator exhaustion.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/29xxx/CVE-2025-29484.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-29484
- https://github.com/libming/libming/issues/330
