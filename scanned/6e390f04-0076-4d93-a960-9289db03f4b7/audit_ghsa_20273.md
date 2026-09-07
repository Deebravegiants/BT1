# [M] Externally Controlled Reference to a Resource in Another Sphere in ruby-mysql

## Summary
Severity: Medium
Advisory: GHSA-73pr-g6jj-5hc9
CVE: CVE-2021-3779
CWE: CWE-610
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-06-29
Source: https://github.com/advisories/GHSA-73pr-g6jj-5hc9
Type: github-advisory

## Affected
- RubyGems: `ruby-mysql` — affected >=0 <2.10.0

## Details
A malicious actor can read arbitrary files from a client that uses ruby-mysql to communicate to a rogue MySQL server and issue database queries. In these cases, the server has the option to create a database reply using the LOAD DATA LOCAL statement, which instructs the client to provide additional data from a local file readable by the client (and not a "local" file on the server).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3779
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/ruby-mysql/CVE-2021-3779.yml
- https://www.rapid7.com/blog/post/2022/06/28/cve-2021-3779-ruby-mysql-gem-client-file-read-fixed
- http://github.com/tmtm/ruby-mysql
