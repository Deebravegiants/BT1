# [H] pyOpenSSL DTLS cookie callback buffer overflow

## Summary
Severity: High
Advisory: GHSA-5pwr-322w-8jr4
CVE: CVE-2026-27459
CWE: CWE-120
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-5pwr-322w-8jr4
Type: github-advisory

## Affected
- PyPI: `pyopenssl` — affected >=22.0.0 <26.0.0

## Details
If a user provided callback to `set_cookie_generate_callback` returned a cookie value greater than 256 bytes, pyOpenSSL would overflow an OpenSSL provided buffer.

Cookie values that are too long are now rejected.

## References
- https://github.com/pyca/pyopenssl/security/advisories/GHSA-5pwr-322w-8jr4
- https://nvd.nist.gov/vuln/detail/CVE-2026-27459
- https://github.com/pyca/pyopenssl/commit/57f09bb4bb051d3bc2a1abd36e9525313d5cd408
- https://github.com/pyca/pyopenssl
- https://github.com/pyca/pyopenssl/blob/358cbf29c4e364c59930e53a270116249581eaa3/CHANGELOG.rst
