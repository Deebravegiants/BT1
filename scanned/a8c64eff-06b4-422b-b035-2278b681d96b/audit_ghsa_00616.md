# [M] Loofah Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-g4xq-jx4w-4cjv
CVE: CVE-2018-16468
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-11-01
Source: https://github.com/advisories/GHSA-g4xq-jx4w-4cjv
Type: github-advisory

## Affected
- RubyGems: `loofah` — affected >=0 <2.2.3

## Details
In the Loofah gem for Ruby, through version 2.2.2, unsanitized JavaScript may occur in sanitized output when a crafted SVG element is republished. Users are advised to upgrade to version 2.2.3.

See https://github.com/flavorjones/loofah/issues/154 for more details.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16468
- https://github.com/flavorjones/loofah/issues/154
- https://github.com/flavorjones/loofah
- https://www.debian.org/security/2019/dsa-4364
