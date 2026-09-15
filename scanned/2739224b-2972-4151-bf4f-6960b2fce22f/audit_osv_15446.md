# [H] CVE-2019-16281

## Summary
Severity: High
Advisory: CVE-2019-16281
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-12-30
Source: https://osv.dev/vulnerability/CVE-2019-16281
Type: osv

## Details
Ptarmigan before 0.2.3 lacks API token validation, e.g., an "if (token === apiToken) {return true;} return false;" code block.

## References
- https://github.com/nayutaco/ptarmigan/releases/tag/v0.2.3
- https://github.com/nayutaco/ptarmigan/commit/37fd8f9da3bab9d323ddd77f2fd20b6dde8bcf6c
- https://github.com/nayutaco/ptarmigan/compare/v0.2.2...v0.2.3
