# [H] Rendertron discloses absolute paths of files

## Summary
Severity: High
Advisory: GHSA-vqmr-957g-r7w3
CVE: CVE-2017-18355
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-02-12
Source: https://github.com/advisories/GHSA-vqmr-957g-r7w3
Type: github-advisory

## Affected
- npm: `rendertron` — affected >=0 <1.1.0

## Details
Installed packages are exposed by node_modules in Rendertron 1.0.0, allowing remote attackers to read absolute paths on the server by examining the "_where" attribute of package.json files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18355
- https://github.com/GoogleChrome/rendertron/pull/88
- https://github.com/GoogleChrome/rendertron/commit/8d70628c96ae72eff6eebb451d26fc9ed6b58b0e
- https://bugs.chromium.org/p/chromium/issues/detail?id=759111
- https://github.com/GoogleChrome/rendertron
- https://github.com/advisories/GHSA-vqmr-957g-r7w3
