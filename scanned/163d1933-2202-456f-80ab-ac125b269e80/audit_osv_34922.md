# [H] ConvertX has Path Traversal that leads to Arbitrary File Write and Arbitrary Code Execution

## Summary
Severity: High
Advisory: CVE-2025-66449
Aliases: GHSA-cpww-gwgc-p72r
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-66449
Type: osv

## Details
ConvertXis a self-hosted online file converter. In versions prior to 0.16.0, the endpoint `/upload` allows an authenticated user to write arbitrary files on the system, overwriting binaries and allowing code execution. The upload function takes `file.name` directly from user supplied data without doing any sanitization on the name thus allowing for arbitrary file write. This can be used to overwrite system binaries with ones provided from an attacker allowing full code execution. Version 0.16.0 contains a patch for the issue.

## References
- https://github.com/C4illin/ConvertX/blob/4ae2aab66ace7cdcc14c5a16ecaaf2372b9ccbdf/src/pages/upload.tsx#L27-L30
- https://github.com/C4illin/ConvertX/security/advisories/GHSA-cpww-gwgc-p72r
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66449.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-66449
- https://github.com/C4illin/ConvertX/commit/550f472451755d095cf5802bc91f403e85b7129e
