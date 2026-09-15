# [H] Bundled libwebp in pywebp vulnerable

## Summary
Severity: High
Advisory: GHSA-f9pm-4g9p-6vm3
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-06
Source: https://github.com/advisories/GHSA-f9pm-4g9p-6vm3
Type: github-advisory

## Affected
- PyPI: `webp` — affected >=0 <0.3.0

## Details
### Impact
pywebp versions before v0.3.0 bundled libwebp binaries in wheels that are vulnerable to CVE-2023-4863. The vulnerability was a heap buffer overflow which allowed a remote attacker to perform an out of bounds memory write.

### Patches
The problem has been patched upstream in libwebp 1.3.2.
pywebp was updated to bundle a patched version of libwebp in v0.3.0.

### Workarounds
No known workarounds without upgrading.

### References
- https://www.rezilion.com/blog/rezilion-researchers-uncover-new-details-on-severity-of-google-chrome-zero-day-vulnerability-cve-2023-4863/
- https://nvd.nist.gov/vuln/detail/CVE-2023-4863

## References
- https://github.com/anibali/pywebp/security/advisories/GHSA-f9pm-4g9p-6vm3
- https://github.com/anibali/pywebp/commit/1f938731a158a6584977cec2cce21b21c15f6c4b
- https://github.com/anibali/pywebp
