# [H] Rails Active Storage has possible Path Traversal in DiskService

## Summary
Severity: High
Advisory: GHSA-9xrj-h377-fr87
CVE: CVE-2026-33195
CWE: CWE-22
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-9xrj-h377-fr87
Type: github-advisory

## Affected
- RubyGems: `activestorage` — affected >=8.1.0.beta1 <8.1.2.1
- RubyGems: `activestorage` — affected >=8.0.0.beta1 <8.0.4.1
- RubyGems: `activestorage` — affected >=0 <7.2.3.1

## Details
### Impact
Active Storage's `DiskService#path_for` does not validate that the resolved filesystem path remains within the storage root directory. If a blob key containing path traversal sequences (e.g. `../`) is used, it could allow reading, writing, or deleting arbitrary files on the server. Blob keys are expected to be trusted strings, but some applications could be passing user input as keys and would be affected.

### Releases
The fixed releases are available at the normal locations.

### Credit
This issue was responsibly reported by Hackerone researcher [ksw9722](https://hackerone.com/ksw9722).

## References
- https://github.com/rails/rails/security/advisories/GHSA-9xrj-h377-fr87
- https://nvd.nist.gov/vuln/detail/CVE-2026-33195
- https://github.com/rails/rails/commit/4933c1e3b8c1bb04925d60347be9f69270392f2c
- https://github.com/rails/rails/commit/9b06fbc0f504b8afe333f33d19548f3b85fbe655
- https://github.com/rails/rails/commit/a290c8a1ec189d793aa6d7f2570b6a763f675348
- https://github.com/rails/rails
- https://github.com/rails/rails/releases/tag/v7.2.3.1
- https://github.com/rails/rails/releases/tag/v8.0.4.1
- https://github.com/rails/rails/releases/tag/v8.1.2.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activestorage/CVE-2026-33195.yml
