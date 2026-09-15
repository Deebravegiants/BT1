# [M] CVE-2025-65797

## Summary
Severity: Medium
Advisory: CVE-2025-65797
Aliases: GHSA-99m2-qwx6-2w6f, GO-2025-4220
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2025-65797
Type: osv

## Details
Incorrect access control in the Identity Provider service of usememos memos v0.25.2 allows attackers with low-level privileges to arbitrarily modify or delete registered identity providers, leading to an account takeover or Denial of Service (DoS).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65797.json
- https://herolab.usd.de/security-advisories/usd-2025-0057/
- https://nvd.nist.gov/vuln/detail/CVE-2025-65797
- https://github.com/usememos/memos/pull/5217
