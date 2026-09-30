# [H] Quivr unauthenticated Denial of Service (DoS) via Multipart Boundary

## Summary
Severity: High
Advisory: GHSA-m76r-xqqj-mqmv
CVE: CVE-2024-9229
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-m76r-xqqj-mqmv
Type: github-advisory

## Affected
- PyPI: `quivr-core` — affected >=0

## Details
A Denial of Service (DoS) vulnerability in the file upload feature of stangirard/quivr v0.0.298 allows unauthenticated attackers to cause excessive resource consumption by appending characters to the end of a multipart boundary in an HTTP request. This leads to the server continuously processing each character, rendering the service unavailable and impacting all users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9229
- https://github.com/QuivrHQ/quivr
- https://github.com/QuivrHQ/quivr/blob/6b07a63e4e969d003710d6f6c6b9df36fd6ea803/backend/api/quivr_api/modules/upload/service/upload_file.py#L68-L101
- https://huntr.com/bounties/946a412d-422f-4623-bb1d-d2646ad23dfd
