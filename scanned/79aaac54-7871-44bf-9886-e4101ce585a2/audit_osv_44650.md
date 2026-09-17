# [M] rubyzip before 3.4.0 Path Traversal in Zip::Entry#extract via Sibling-Directory Prefix

## Summary
Severity: Medium
Advisory: CVE-2026-85396
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85396
Type: osv

## Details
rubyzip versions before 3.4.0 contain a path traversal vulnerability in Zip::Entry#extract that fails to properly validate extraction paths using prefix comparison without trailing separators. Attackers can craft archive entries with names like ../upload_backup/owned.sh to write files outside the intended extraction directory into sibling paths sharing the destination prefix.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85396.json
- https://github.com/rubyzip/rubyzip/releases/tag/v3.4.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-85396
- https://www.vulncheck.com/advisories/rubyzip-before-3.4.0-path-traversal-in-zip-entry-extract-via-sibling-directory-prefix
- https://github.com/rubyzip/rubyzip/commit/17edfbf4423b83211b075acc23a7d8640da63449
- https://github.com/rubyzip/rubyzip
- https://github.com/geo-chen/oss/blob/main/rubyzip.md
- https://github.com/rubyzip/rubyzip/blob/v3.3.1/lib/zip/entry.rb
