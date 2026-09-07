# [M] Avo has a XSS vulnerability on `return_to` param

## Summary
Severity: Medium
Advisory: GHSA-762r-27w2-q22j
CVE: CVE-2026-33209
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-762r-27w2-q22j
Type: github-advisory

## Affected
- RubyGems: `avo` — affected >=0 <3.30.3

## Details
## Description

A reflected cross-site scripting (XSS) vulnerability exists in the `return_to` query parameter used in the avo interface.

An attacker can craft a malicious URL that injects arbitrary JavaScript, which is executed when he clicks a dynamically generated navigation button.

## Impact

This vulnerability may allow execution of arbitrary JavaScript in the context of the application.

Impact varies depending on deployment:
- In unauthenticated setups: exploitable via crafted links sent to users
- In authenticated setups: limited to authenticated users and requires interaction

## References
- https://github.com/avo-hq/avo/security/advisories/GHSA-762r-27w2-q22j
- https://nvd.nist.gov/vuln/detail/CVE-2026-33209
- https://github.com/avo-hq/avo/pull/4330
- https://github.com/avo-hq/avo/commit/4453d39ddc6309f3bc8ada73ef21e1971112de7d
- https://github.com/avo-hq/avo
- https://github.com/avo-hq/avo/releases/tag/v3.30.3
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/avo/CVE-2026-33209.yml
