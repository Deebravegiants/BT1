# [H] @conform-to/dom parseSubmission vulnerable to CPU exhaustion when parsing many unique form fields

## Summary
Severity: High
Advisory: GHSA-525m-7f82-2mf7
CVE: CVE-2026-49250
CWE: CWE-407
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-525m-7f82-2mf7
Type: github-advisory

## Affected
- npm: `@conform-to/dom` — affected >=1.8.0 <1.19.4

## Details
A CPU exhaustion vulnerability exists in Conform's [`parseSubmission`](https://conform.guide/api/react/future/parseSubmission) future API when parsing `FormData` or `URLSearchParams` submissions with many unique field names. The parser previously looked up values by field name, which could require repeated scans of the submitted entries and cause excessive synchronous CPU work if an attacker supplies a crafted submission.

> [!NOTE]
> The patched version fixes this by iterating submitted entries directly instead of repeatedly looking up values by field name. Applications that accept untrusted form submissions should still enforce request parsing limits before passing data to Conform. For multipart requests, [@remix-run/form-data-parser](https://www.npmjs.com/package/@remix-run/form-data-parser) provides `maxParts`, `maxTotalSize`, `maxFileSize`, `maxFiles`, and `maxHeaderSize` options.

## References
- https://github.com/edmundhung/conform/security/advisories/GHSA-525m-7f82-2mf7
- https://github.com/edmundhung/conform
