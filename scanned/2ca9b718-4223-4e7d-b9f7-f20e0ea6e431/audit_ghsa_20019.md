# [H] Uncontrolled Recursion in Loofah

## Summary
Severity: High
Advisory: GHSA-3x8r-x6xp-q4vm
CVE: CVE-2022-23516
CWE: CWE-674
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-12-13
Source: https://github.com/advisories/GHSA-3x8r-x6xp-q4vm
Type: github-advisory

## Affected
- RubyGems: `loofah` — affected >=2.2.0 <2.19.1

## Details
## Summary

Loofah `>= 2.2.0, < 2.19.1` uses recursion for sanitizing `CDATA` sections, making it susceptible to stack exhaustion and raising a `SystemStackError` exception.  This may lead to a denial of service through CPU resource consumption.


## Mitigation

Upgrade to Loofah `>= 2.19.1`.

Users who are unable to upgrade may be able to mitigate this vulnerability by limiting the length of the strings that are sanitized.


## Severity

The Loofah maintainers have evaluated this as [High Severity 7.5 (CVSS3.1)](https://www.first.org/cvss/calculator/3.1#CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H).


## References

- [CWE - CWE-674: Uncontrolled Recursion (4.9)](https://cwe.mitre.org/data/definitions/674.html)

## References
- https://github.com/flavorjones/loofah/security/advisories/GHSA-3x8r-x6xp-q4vm
- https://nvd.nist.gov/vuln/detail/CVE-2022-23516
- https://github.com/flavorjones/loofah/commit/86f7f6364491b0099d215db858ecdc0c89ded040
- https://github.com/flavorjones/loofah
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/loofah/CVE-2022-23516.yml
- https://lists.debian.org/debian-lts-announce/2023/09/msg00011.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00044.html
