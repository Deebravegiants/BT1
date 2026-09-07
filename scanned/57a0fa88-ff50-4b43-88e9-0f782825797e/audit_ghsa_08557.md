# [M] instagrapi: Unsafe signup challenge path handling in instagrapi

## Summary
Severity: Medium
Advisory: GHSA-ggxf-37hm-9wqf
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-23
Source: https://github.com/advisories/GHSA-ggxf-37hm-9wqf
Type: github-advisory

## Affected
- PyPI: `instagrapi` — affected >=0 <2.6.9

## Details
instagrapi versions before 2.6.9 accepted server-supplied signup challenge paths and used them to build request URLs before validating that the paths were relative Instagram API paths. A malicious or tampered challenge payload could cause challenge handling requests to be sent outside the intended Instagram host with the client\'s existing session headers. Version 2.6.9 validates challenge paths before building URLs, solving captcha challenges, or submitting phone/SMS challenge forms.

## References
- https://github.com/subzeroid/instagrapi/security/advisories/GHSA-ggxf-37hm-9wqf
- https://github.com/subzeroid/instagrapi
