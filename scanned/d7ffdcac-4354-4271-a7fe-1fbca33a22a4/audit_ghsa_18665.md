# [M] cryptidy allows code execution via untrusted data due to pickle.loads 

## Summary
Severity: Medium
Advisory: GHSA-97w9-v595-3h5q
CVE: CVE-2025-63675
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2025-10-31
Source: https://github.com/advisories/GHSA-97w9-v595-3h5q
Type: github-advisory

## Affected
- PyPI: `cryptidy` — affected >=0

## Details
cryptidy through 1.2.4 allows code execution via untrusted data because pickle.loads is used. This occurs in aes_decrypt_message in symmetric_encryption.py.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-63675
- https://github.com/javiermorales36/cryptidy-analysis
- https://github.com/netinvent/cryptidy
- https://github.com/netinvent/cryptidy/blob/cebc9ffd54cc20679d15a1a43ca9a5da645b0c58/cryptidy/symmetric_encryption.py#L220-L238
