# [H] CVE-2025-66692

## Summary
Severity: High
Advisory: CVE-2025-66692
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-20
Source: https://osv.dev/vulnerability/CVE-2025-66692
Type: osv

## Details
A buffer over-read in the PublicKey::verify() method of Binance - Trust Wallet Core before commit 5668c67 allows attackers to cause a Denial of Service (DoS) via a crafted input.

## References
- https://gist.github.com/inkman97/b791189338f73b758c31a7db3cd50c2d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66692.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-66692
- https://github.com/trustwallet/wallet-core/commit/5668c67
