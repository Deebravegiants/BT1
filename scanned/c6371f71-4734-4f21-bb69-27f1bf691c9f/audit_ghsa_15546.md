# [H] Heap-based Buffer Overflow in sqlite-vec

## Summary
Severity: High
Advisory: GHSA-vrcx-gx3g-j3h8
CVE: CVE-2024-46488
CWE: CWE-122, CWE-787
Ecosystem: PyPI, RubyGems, crates.io, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2024-09-25
Source: https://github.com/advisories/GHSA-vrcx-gx3g-j3h8
Type: github-advisory

## Affected
- PyPI: `sqlite-vec` — affected >=0 <0.1.3
- npm: `sqlite-vec` — affected >=0 <0.1.3
- RubyGems: `sqlite-vec` — affected >=0 <0.1.3
- crates.io: `sqlite-vec` — affected >=0 <0.1.3

## Details
sqlite-vec v0.1.1 was discovered to contain a heap buffer overflow via the npy_token_next function. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-46488
- https://github.com/VulnSphere/LLMVulnSphere/blob/main/VectorDB/sqlite-vec/OOBR_2.md
- https://github.com/advisories/GHSA-vrcx-gx3g-j3h8
- https://github.com/asg017/sqlite-vec
- https://github.com/asg017/sqlite-vec/releases/tag/v0.1.3
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/sqlite-vec/CVE-2024-46488.yml
