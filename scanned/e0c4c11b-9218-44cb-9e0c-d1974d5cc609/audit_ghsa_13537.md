# [M] svg_optimizer rubygem external XML entity (XXE) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6hvg-62q8-95v7
CVE: CVE-2023-46035
CWE: CWE-611
Ecosystem: RubyGems
Published: 2023-10-20
Source: https://github.com/advisories/GHSA-6hvg-62q8-95v7
Type: github-advisory

## Affected
- RubyGems: `svg_optimizer` — affected >=0.2.6 <0.3.0

## Details
An issue in Fnando svg_optimizer v.0.2.6 allows a remote attacker to escalate privileges when optimizing untrusted SVG content.

## References
- https://github.com/fnando/svg_optimizer/pull/17
- https://github.com/fnando/svg_optimizer/commit/8244ff25b51a16892496e9d9f7191dba393f7af0
- https://github.com/fnando/svg_optimizer/commit/b1b5013db297494daba5676b9fa4423ffc5e96fa
- https://github.com/fnando/svg_optimizer
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/svg_optimizer/CVE-2023-46035.yml
