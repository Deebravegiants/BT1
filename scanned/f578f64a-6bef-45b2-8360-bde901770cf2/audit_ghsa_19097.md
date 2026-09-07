# [H] @rpldy/uploader prototype pollution

## Summary
Severity: High
Advisory: GHSA-pc47-g7gv-4gpw
CVE: CVE-2024-57082
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-02-06
Source: https://github.com/advisories/GHSA-pc47-g7gv-4gpw
Type: github-advisory

## Affected
- npm: `@rpldy/uploader` — affected >=0 <1.9.1

## Details
A prototype pollution in the lib.createUploader function of @rpldy/uploader v1.8.1 allows attackers to cause a Denial of Service (DoS) via supplying a crafted payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-57082
- https://github.com/rpldy/react-uploady/commit/386e0a80c428eb988e89fd2acf9bb0b786ac8028
- https://gist.github.com/tariqhawis/708e518de0c3b5af7430ec774f68f315
- https://github.com/rpldy/react-uploady
- https://github.com/rpldy/react-uploady/releases/tag/v1.9.1
