# [H] Code injection in ruby git

## Summary
Severity: High
Advisory: GHSA-pphf-gfrm-v32r
CVE: CVE-2022-47318
CWE: CWE-94
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-17
Source: https://github.com/advisories/GHSA-pphf-gfrm-v32r
Type: github-advisory

## Affected
- RubyGems: `git` — affected >=0 <1.13.0

## Details
ruby-git versions prior to v1.13.0 allows a remote authenticated attacker to execute an arbitrary ruby code by having a user to load a repository containing a specially crafted filename to the product. This vulnerability is different from CVE-2022-46648.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-47318
- https://github.com/ruby-git/ruby-git/pull/602
- https://github.com/ruby-git/ruby-git
- https://jvn.jp/en/jp/JVN16765254/index.html
- https://lists.debian.org/debian-lts-announce/2023/01/msg00043.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4KPFLSZPUM7APWVBRM5DCAY5OUVQBF4K
