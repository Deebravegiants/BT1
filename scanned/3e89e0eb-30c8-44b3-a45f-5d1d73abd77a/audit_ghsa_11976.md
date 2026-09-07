# [M] Rails Active Support has a possible XSS vulnerability in SafeBuffer#%

## Summary
Severity: Medium
Advisory: GHSA-89vf-4333-qx8v
CVE: CVE-2026-33170
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-89vf-4333-qx8v
Type: github-advisory

## Affected
- RubyGems: `activesupport` — affected >=8.1.0.beta1 <8.1.2.1
- RubyGems: `activesupport` — affected >=8.0.0.beta1 <8.0.4.1
- RubyGems: `activesupport` — affected >=0 <7.2.3.1

## Details
### Impact
`SafeBuffer#%` does not propagate the `@html_unsafe` flag to the newly created buffer. If a `SafeBuffer` is mutated in place (e.g. via `gsub!`) and then formatted with `%` using untrusted arguments, the result incorrectly reports `html_safe? == true`, bypassing ERB auto-escaping and possibly leading to XSS.

### Releases
The fixed releases are available at the normal locations.

### Credit
This issue was responsibly reported by @ch4n3-yoon

## References
- https://github.com/rails/rails/security/advisories/GHSA-89vf-4333-qx8v
- https://nvd.nist.gov/vuln/detail/CVE-2026-33170
- https://github.com/rails/rails/commit/50d732af3b7c8aaf63cbcca0becbc00279b215b7
- https://github.com/rails/rails/commit/6e8a81108001d58043de9e54a06fca58962fc2db
- https://github.com/rails/rails/commit/c1ad0e8e1972032f3395853a5e99cea035035beb
- https://github.com/rails/rails
- https://github.com/rails/rails/releases/tag/v7.2.3.1
- https://github.com/rails/rails/releases/tag/v8.0.4.1
- https://github.com/rails/rails/releases/tag/v8.1.2.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activesupport/CVE-2026-33170.yml
