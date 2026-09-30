# [H] Eugeny Tabby Sends Password Despite Host Key Verification Failure

## Summary
Severity: High
Advisory: GHSA-8vq4-8hfp-29xh
CVE: CVE-2024-48460
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-01-17
Source: https://github.com/advisories/GHSA-8vq4-8hfp-29xh
Type: github-advisory

## Affected
- npm: `tabby-ssh` — affected >=0 <1.0.214

## Details
An issue in Eugeny Tabby 1.0.213 allows a remote attacker to obtain sensitive information via the server and sends the SSH username and password even when the host key verification fails.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-48460
- https://github.com/Eugeny/tabby/issues/9955
- https://github.com/Eugeny/tabby/commit/1c077147acd0a6ec9f8ee80d83a3e9688fbb9444
- https://github.com/Eugeny/tabby
