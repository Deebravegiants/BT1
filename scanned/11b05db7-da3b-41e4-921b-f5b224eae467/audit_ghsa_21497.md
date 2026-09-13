# [H] Sinatra vulnerable to Reflected File Download attack

## Summary
Severity: High
Advisory: GHSA-2x8x-jmrp-phxw
CVE: CVE-2022-45442
CWE: CWE-494
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-30
Source: https://github.com/advisories/GHSA-2x8x-jmrp-phxw
Type: github-advisory

## Affected
- RubyGems: `sinatra` — affected >=3.0 <3.0.4
- RubyGems: `sinatra` — affected >=2.0.0 <2.2.3

## Details
### Description
An issue was discovered in Sinatra 2.0 before 2.2.3 and 3.0 before 3.0.4. An application is vulnerable to a reflected file download (RFD) attack that sets the Content-Disposition header of a response when the filename is derived from user-supplied input.

### References
* https://www.blackhat.com/docs/eu-14/materials/eu-14-Hafif-Reflected-File-Download-A-New-Web-Attack-Vector.pdf
* https://github.com/advisories/GHSA-8x94-hmjh-97hq

## References
- https://github.com/sinatra/sinatra/security/advisories/GHSA-2x8x-jmrp-phxw
- https://nvd.nist.gov/vuln/detail/CVE-2022-45442
- https://github.com/sinatra/sinatra/commit/ea8fc9495a350f7551b39e3025bfcd06f49f363b
- https://github.com/advisories/GHSA-8x94-hmjh-97hq
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/sinatra/CVE-2022-45442.yml
- https://github.com/sinatra/sinatra
- https://lists.debian.org/debian-lts-announce/2023/01/msg00005.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00020.html
- https://www.blackhat.com/docs/eu-14/materials/eu-14-Hafif-Reflected-File-Download-A-New-Web-Attack-Vector.pdf
