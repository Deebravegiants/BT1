# [M] Loofah Allows Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-c3gv-9cxf-6f57
CVE: CVE-2019-15587
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-11-05
Source: https://github.com/advisories/GHSA-c3gv-9cxf-6f57
Type: github-advisory

## Affected
- RubyGems: `loofah` — affected >=0 <2.3.1

## Details
In the Loofah gem for Ruby through v2.3.0, unsanitized JavaScript may occur in sanitized output when a crafted SVG element is republished.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15587
- https://github.com/flavorjones/loofah/issues/171
- https://github.com/flavorjones/loofah/commit/0c6617af440879ce97440f6eb6c58636456dc8ec
- https://hackerone.com/reports/709009
- https://github.com/flavorjones/loofah
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/loofah/CVE-2019-15587.yml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4WK2UG7ORKRQOJ6E4XJ2NVIHYJES6BYZ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XMCWPLYPNIWYAY443IZZJ4IHBBLIHBP5
- https://security.netapp.com/advisory/ntap-20191122-0003
- https://usn.ubuntu.com/4498-1
- https://www.debian.org/security/2019/dsa-4554
