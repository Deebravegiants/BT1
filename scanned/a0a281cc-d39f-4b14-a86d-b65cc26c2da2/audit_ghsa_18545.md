# [M] resolv vulnerable to DoS via insufficient DNS domain name length validation

## Summary
Severity: Medium
Advisory: GHSA-xh69-987w-hrp8
CVE: CVE-2025-24294
CWE: CWE-1284, CWE-400
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-07-15
Source: https://github.com/advisories/GHSA-xh69-987w-hrp8
Type: github-advisory

## Affected
- RubyGems: `resolv` — affected >=0 <0.2.3
- RubyGems: `resolv` — affected >=0.4.0 <0.6.2
- RubyGems: `resolv` — affected >=0.3.0 <0.3.1

## Details
A denial of service vulnerability has been discovered in the resolv gem bundled with Ruby.

## Details
The vulnerability is caused by an insufficient check on the length of a decompressed domain name within a DNS packet.

An attacker can craft a malicious DNS packet containing a highly compressed domain name. When the resolv library parses such a packet, the name decompression process consumes a large amount of CPU resources, as the library does not limit the resulting
length of the name.

This resource consumption can cause the application thread to become unresponsive, resulting in a Denial of Service condition.

## Affected Version
The vulnerability affects the resolv gem bundled with the following Ruby series:
* Ruby 3.2 series: resolv version 0.2.2 and earlier
* Ruby 3.3 series: resolv version 0.3.0
* Ruby 3.4 series: resolv version 0.6.1 and earlier

## Credits
Thanks to Manu for discovering this issue.

## History
Originally published at 2025-07-08 07:00:00 (UTC)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-24294
- https://github.com/ruby/resolv/commit/4c2f71b5e80826506f78417d85b38481c058fb25
- https://github.com/ruby/resolv
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/resolv/CVE-2025-24294.yml
- https://www.ruby-lang.org/en/news/2025/07/08/dos-resolv-cve-2025-24294
