# [H] RubyGems before 4.0.13 Path Traversal via Symlink Resolution

## Summary
Severity: High
Advisory: CVE-2026-82455
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-29
Source: https://osv.dev/vulnerability/CVE-2026-82455
Type: osv

## Details
RubyGems fails to re-validate path containment after filesystem symlink resolution during gem extraction. When a pre-existing symlink inside the destination directory points outside the extraction root, extracted files that appear to be written under the destination directory can instead be written outside of it, breaking the extraction safety boundary. The fix resolves the real path of the parent directory before writing and raises Gem::Package::PathError if it escapes the destination directory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82455.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82455
- https://www.vulncheck.com/advisories/rubygems-before-4.0.13-path-traversal-via-symlink-resolution
- https://github.com/ruby/rubygems/commit/103ca4230deacb31b9fcd813de109e83b5fc71ac
- https://github.com/ruby/rubygems/pull/9493
- https://github.com/ruby/rubygems
