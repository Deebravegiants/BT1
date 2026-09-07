# [M] n8n: Authenticated Users Can Exhaust Temporary Disk Storage via Data-Table File Uploads

## Summary
Severity: Medium
Advisory: GHSA-w867-jm58-p9pv
CVE: CVE-2026-58661
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-w867-jm58-p9pv
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.0.0 <2.28.0
- npm: `n8n` — affected >=0 <1.123.58

## Details
## Impact
An authenticated user can repeatedly upload files to the data-table upload endpoint, bypassing the per-request quota check, which does not account for files already written to the shared temporary directory. This causes temporary files to accumulate on disk until the periodic cleanup runs, potentially exhausting available disk space on the host.

## Patches
Users should upgrade to the patched version once available to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict n8n instance access to fully trusted users only.
- Set `uploadMaxFileSize` to a low value to limit individual upload size.
- Monitor and alert on disk usage in the n8n temporary upload directory.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-w867-jm58-p9pv
- https://nvd.nist.gov/vuln/detail/CVE-2026-58661
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.58
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.28.0
- https://www.vulncheck.com/advisories/n8n-disk-space-exhaustion-via-data-table-file-upload-endpoint
