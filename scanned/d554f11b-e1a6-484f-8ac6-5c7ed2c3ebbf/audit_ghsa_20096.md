# [H] Inefficient Regular Expression Complexity in Loofah

## Summary
Severity: High
Advisory: GHSA-486f-hjj9-9vhh
CVE: CVE-2022-23514
CWE: CWE-1333
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-12-13
Source: https://github.com/advisories/GHSA-486f-hjj9-9vhh
Type: github-advisory

## Affected
- RubyGems: `loofah` — affected >=0 <2.19.1

## Details
## Summary

Loofah `< 2.19.1` contains an inefficient regular expression that is susceptible to excessive backtracking when attempting to sanitize certain SVG attributes. This may lead to a denial of service through CPU resource consumption.


## Mitigation

Upgrade to Loofah `>= 2.19.1`.


## Severity

The Loofah maintainers have evaluated this as [High Severity 7.5 (CVSS3.1)](https://www.first.org/cvss/calculator/3.1#CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H).


## References

- [CWE - CWE-1333: Inefficient Regular Expression Complexity (4.9)](https://cwe.mitre.org/data/definitions/1333.html)
- https://hackerone.com/reports/1684163


## Credit

This vulnerability was responsibly reported by @ooooooo-q (https://github.com/ooooooo-q).

## References
- https://github.com/flavorjones/loofah/security/advisories/GHSA-486f-hjj9-9vhh
- https://nvd.nist.gov/vuln/detail/CVE-2022-23514
- https://github.com/flavorjones/loofah/commit/a6e0a1ab90675a17b1b2be189129d94139e4b143
- https://hackerone.com/reports/1684163
- https://github.com/flavorjones/loofah
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/loofah/CVE-2022-23514.yml
- https://lists.debian.org/debian-lts-announce/2023/09/msg00011.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00044.html
