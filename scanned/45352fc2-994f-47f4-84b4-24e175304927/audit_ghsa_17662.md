# [H] Octo STS Unauthenticated SSRF by abusing fields in OpenID Connect tokens

## Summary
Severity: High
Advisory: GHSA-h3qp-hwvr-9xcq
CVE: CVE-2025-52477
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-06-26
Source: https://github.com/advisories/GHSA-h3qp-hwvr-9xcq
Type: github-advisory

## Affected
- Go: `github.com/octo-sts/app` — affected >=0 <0.5.3

## Details
##  Summary

Octo-STS versions before v0.5.3 are vulnerable to unauthenticated SSRF by abusing fields in OpenID Connect tokens. Malicious tokens were shown to trigger internal network requests which could reflect error logs with sensitive information. 

Please upgrade to v0.5.3 to resolve this issue. This version includes patch sets to [sanitize input](https://github.com/octo-sts/app/commit/b3976e39bd8c8c217c0670747d34a4499043da92) and [redact logging](https://github.com/octo-sts/app/commit/0f177fde54f9318e33f0bba6abaea9463a7c3afd).

Many thanks to @vicevirus for reporting this issue and for assisting with remediation review.

## References

- https://github.com/octo-sts/app/security/advisories/GHSA-h3qp-hwvr-9xcq
- https://github.com/octo-sts/app/commit/b3976e39bd8c8c217c0670747d34a4499043da92
- https://github.com/octo-sts/app/commit/0f177fde54f9318e33f0bba6abaea9463a7c3afd

## References
- https://github.com/octo-sts/app/security/advisories/GHSA-h3qp-hwvr-9xcq
- https://nvd.nist.gov/vuln/detail/CVE-2025-52477
- https://github.com/octo-sts/app/commit/0f177fde54f9318e33f0bba6abaea9463a7c3afd
- https://github.com/octo-sts/app/commit/b3976e39bd8c8c217c0670747d34a4499043da92
- https://github.com/octo-sts/app
