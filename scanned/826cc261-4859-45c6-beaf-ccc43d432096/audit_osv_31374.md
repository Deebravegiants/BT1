# [H] SSRF Check Bypass in Requests Utility in significant-gravitas/autogpt

## Summary
Severity: High
Advisory: CVE-2025-0454
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2025-0454
Type: osv

## Details
A Server-Side Request Forgery (SSRF) vulnerability was identified in the Requests utility of significant-gravitas/autogpt versions prior to v0.4.0. The vulnerability arises due to a hostname confusion between the `urlparse` function from the `urllib.parse` library and the `requests` library. A malicious user can exploit this by submitting a specially crafted URL, such as `http://localhost:\@google.com/../`, to bypass the SSRF check and perform an SSRF attack.

## References
- https://huntr.com/bounties/0664fdee-bdc2-4650-8075-74d7b8d3e308
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/0xxx/CVE-2025-0454.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-0454
- https://github.com/significant-gravitas/autogpt/commit/ff065cd24c2289878c0abdb9adbf91c305f0d70a
