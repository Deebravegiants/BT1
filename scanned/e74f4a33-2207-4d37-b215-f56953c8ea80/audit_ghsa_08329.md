# [M] aiograpi: Unsafe signup challenge path handling

## Summary
Severity: Medium
Advisory: GHSA-jh37-x3fv-4x72
CVE: CVE-2026-47157
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-23
Source: https://github.com/advisories/GHSA-jh37-x3fv-4x72
Type: github-advisory

## Affected
- PyPI: `aiograpi` — affected >=0 <0.9.10

## Details
aiograpi versions before 0.9.10 accepted server-supplied signup challenge paths and used them to build request URLs before validating that the paths were relative Instagram API paths. A malicious or tampered challenge payload could cause challenge handling requests to be sent outside the intended Instagram host with the client\'s existing session headers. Version 0.9.10 validates challenge paths before building URLs, solving captcha challenges, or submitting phone/SMS challenge forms.

## References
- https://github.com/subzeroid/aiograpi/security/advisories/GHSA-jh37-x3fv-4x72
- https://nvd.nist.gov/vuln/detail/CVE-2026-47157
- https://github.com/subzeroid/aiograpi/pull/274
- https://github.com/subzeroid/aiograpi/commit/9c24151916beca622e588bfb3167c98711ff744f
- https://github.com/subzeroid/aiograpi
- https://github.com/subzeroid/aiograpi/releases/tag/0.9.10
