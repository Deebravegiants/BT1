# [H] CVE-2023-37029

## Summary
Severity: High
Advisory: CVE-2023-37029
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-21
Source: https://osv.dev/vulnerability/CVE-2023-37029
Type: osv

## Details
Magma versions <= 1.8.0 (fixed in v1.9 commit 08472ba98b8321f802e95f5622fa90fec2dea486) are susceptible to an assertion-based crash when an oversized NAS packet is received. An attacker may leverage this behavior to repeatedly crash the MME via either a compromised base station or via an unauthenticated cellphone within range of a base station managed by the MME, causing a denial of service.

## References
- https://cellularsecurity.org/ransacked
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/37xxx/CVE-2023-37029.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-37029
