# [M] Rails Active Storage has a possible DoS vulnerability when in proxy mode via Range requests

## Summary
Severity: Medium
Advisory: GHSA-r46p-8f7g-vvvg
CVE: CVE-2026-33174
CWE: CWE-789
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-r46p-8f7g-vvvg
Type: github-advisory

## Affected
- RubyGems: `activestorage` — affected >=8.1.0.beta1 <8.1.2.1
- RubyGems: `activestorage` — affected >=8.0.0.beta1 <8.0.4.1
- RubyGems: `activestorage` — affected >=0 <7.2.3.1

## Details
### Impact
When serving files through Active Storage's `Blobs::ProxyController`, the controller loads the entire requested byte range into memory before sending it. A request with a large or unbounded Range header (e.g. `bytes=0-`) could cause the server to allocate memory proportional to the file size, possibly resulting in a DoS vulnerability through memory exhaustion.

### Releases
The fixed releases are available at the normal locations.

### Credit
This issue was responsibly reported by Hackerone user [pirikara](https://hackerone.com/pirikara)

## References
- https://github.com/rails/rails/security/advisories/GHSA-r46p-8f7g-vvvg
- https://nvd.nist.gov/vuln/detail/CVE-2026-33174
- https://github.com/rails/rails/commit/2cd933c366b777f873d4d590127da2f4a25e4ba5
- https://github.com/rails/rails/commit/42012eaaa88dfc7d0030161b2bc8074a7bbce92a
- https://github.com/rails/rails/commit/8159a9c3de3f27a2bcf2866b8bf9ceb9075e229b
- https://github.com/rails/rails
- https://github.com/rails/rails/releases/tag/v7.2.3.1
- https://github.com/rails/rails/releases/tag/v8.0.4.1
- https://github.com/rails/rails/releases/tag/v8.1.2.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activestorage/CVE-2026-33174.yml
