# [M] CVE-2025-48027

## Summary
Severity: Medium
Advisory: CVE-2025-48027
CVSS: 5.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2025-05-15
Source: https://osv.dev/vulnerability/CVE-2025-48027
Type: osv

## Details
The HttpAuth plugin in pGina.Fork through 3.9.9.12 allows authentication bypass when an adversary controls DNS resolution for pginaloginserver.

## References
- https://github.com/MutonUfoAI/pgina/blob/1922de0fe27492c09d2f188c2c7e54a4b364bbad/Plugins/HttpAuth/HttpAuth/Settings.cs#L44
- https://github.com/kwburns/CVE/blob/main/pGina.Fork/3.9.9.12/README.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48027.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-48027
