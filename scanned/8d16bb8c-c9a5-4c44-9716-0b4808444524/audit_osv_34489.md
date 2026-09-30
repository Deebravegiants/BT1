# [M] CVE-2025-60935

## Summary
Severity: Medium
Advisory: CVE-2025-60935
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2025-60935
Type: osv

## Details
An open redirect vulnerability in the login endpoint of Blitz Panel v1.17.0 allows attackers to redirect users to malicious domains via a crafted URL. This issue affects the next_url parameter in the login endpoint and could lead to phishing or token theft after successful authentication.

## References
- https://gist.github.com/HEXER365/2e866b47d56585e1e59e7c16bf4b4db7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/60xxx/CVE-2025-60935.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-60935
- https://github.com/ReturnFI/Blitz
