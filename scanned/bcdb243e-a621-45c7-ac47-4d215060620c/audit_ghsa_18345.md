# [M] Parcel has an Origin Validation Error vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qm9p-f9j5-w83w
CVE: CVE-2025-56648
CWE: CWE-346
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-09-17
Source: https://github.com/advisories/GHSA-qm9p-f9j5-w83w
Type: github-advisory

## Affected
- npm: `@parcel/reporter-dev-server` — affected >=1.6.1 <2.16.4

## Details
parcel versions 1.6.1 and above have an Origin Validation Error vulnerability. Malicious websites can send XMLHTTPRequests to the application's development server and read the response to steal source code when developers visit them. Version 2.16.4 supports a `--no-cors` option which disables CORS headers in the dev server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-56648
- https://github.com/parcel-bundler/parcel/issues/10216
- https://github.com/parcel-bundler/parcel/pull/10138
- https://github.com/parcel-bundler/parcel/commit/4bc56e3242a85491c7edf589966e9b44c6330c49
- https://github.com/parcel-bundler/parcel/commit/9e2f6f1377123cff3b82f6dde4e20336efc846a1
- https://gist.github.com/R4356th/41f468def606b2406e36f7193f5322b8
- https://github.com/parcel-bundler/parcel
- https://github.com/parcel-bundler/parcel/discussions/10089
