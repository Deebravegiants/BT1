# [M] Werkzeug safe_join not safe on Windows

## Summary
Severity: Medium
Advisory: GHSA-f9vj-2wh5-fj8j
CVE: CVE-2024-49766
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-10-25
Source: https://github.com/advisories/GHSA-f9vj-2wh5-fj8j
Type: github-advisory

## Affected
- PyPI: `Werkzeug` — affected >=0 <3.0.6

## Details
On Python < 3.11 on Windows, `os.path.isabs()` does not catch UNC paths like `//server/share`. Werkzeug's `safe_join()` relies on this check, and so can produce a path that is not safe, potentially allowing unintended access to data. Applications using Python >= 3.11, or not using Windows, are not vulnerable.

## References
- https://github.com/pallets/werkzeug/security/advisories/GHSA-f9vj-2wh5-fj8j
- https://nvd.nist.gov/vuln/detail/CVE-2024-49766
- https://github.com/pallets/werkzeug/commit/2767bcb10a7dd1c297d812cc5e6d11a474c1f092
- https://github.com/pallets/werkzeug
- https://github.com/pallets/werkzeug/releases/tag/3.0.6
- https://security.netapp.com/advisory/ntap-20250131-0005
