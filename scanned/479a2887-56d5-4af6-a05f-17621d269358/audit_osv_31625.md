# [H] Admin account takeover through weak Pseudo-Random number generator used in generating password reset codes in langgenius/dify

## Summary
Severity: High
Advisory: CVE-2025-1796
CVSS: 7.5 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2025-1796
Type: osv

## Details
A vulnerability in langgenius/dify v0.10.1 allows an attacker to take over any account, including administrator accounts, by exploiting a weak pseudo-random number generator (PRNG) used for generating password reset codes. The application uses `random.randint` for this purpose, which is not suitable for cryptographic use and can be cracked. An attacker with access to workflow tools can extract the PRNG output and predict future password reset codes, leading to a complete compromise of the application.

## References
- https://huntr.com/bounties/a60f3039-5394-4e22-8de7-a7da9c6a6e00
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/1xxx/CVE-2025-1796.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-1796
