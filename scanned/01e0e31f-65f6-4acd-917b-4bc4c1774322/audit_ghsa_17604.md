# [M] ReDoS Vulnerability in Rack::Multipart handle_mime_head

## Summary
Severity: Medium
Advisory: GHSA-47m2-26rw-j2jw
CVE: CVE-2025-49007
CWE: CWE-770
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-06-05
Source: https://github.com/advisories/GHSA-47m2-26rw-j2jw
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=3.1.0 <3.1.16

## Details
### Summary
There is a denial of service vulnerability in the Content-Disposition parsing component of Rack. This is very similar to the previous security issue CVE-2022-44571.

### Details

Carefully crafted input can cause Content-Disposition header parsing in Rack to take an unexpected amount of time, possibly resulting in a denial of service attack vector. This header is used typically used in multipart parsing. Any applications that parse multipart posts using Rack (virtually all Rails applications) are impacted.

### Credits

Thanks to [scyoon](https://hackerone.com/scyoon) for reporting this to the Rails security team

## References
- https://github.com/rack/rack/security/advisories/GHSA-47m2-26rw-j2jw
- https://nvd.nist.gov/vuln/detail/CVE-2025-49007
- https://github.com/rack/rack/commit/4795831a0a310c2d31102749e551b38faab6401f
- https://github.com/rack/rack/commit/aed514df37e33907df3c971ed3ca9a0a20ac2901
- https://github.com/rack/rack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2025-49007.yml
