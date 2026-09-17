# [M] Requests `Session` object does not verify requests after making first request with verify=False

## Summary
Severity: Medium
Advisory: GHSA-9wx4-h78v-vm56
CVE: CVE-2024-35195
CWE: CWE-670
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-05-20
Source: https://github.com/advisories/GHSA-9wx4-h78v-vm56
Type: github-advisory

## Affected
- PyPI: `requests` — affected >=0 <2.32.0

## Details
When using a `requests.Session`, if the first request to a given origin is made with `verify=False`, TLS certificate verification may remain disabled for all subsequent requests to that origin, even if `verify=True` is explicitly specified later.

This occurs because the underlying connection is reused from the session's connection pool, causing the initial TLS verification setting to persist for the lifetime of the pooled connection. As a result, applications may unintentionally send requests without certificate verification, leading to potential man-in-the-middle attacks and compromised confidentiality or integrity.

This behavior affects versions of `requests` prior to 2.32.0.

## References
- https://github.com/psf/requests/security/advisories/GHSA-9wx4-h78v-vm56
- https://nvd.nist.gov/vuln/detail/CVE-2024-35195
- https://github.com/psf/requests/pull/6655
- https://github.com/psf/requests/commit/a58d7f2ffb4d00b46dca2d70a3932a0b37e22fac
- https://github.com/psf/requests
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IYLSNK5TL46Q6XPRVMHVWS63MVJQOK4Q
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/N7WP6EYDSUOCOJYHDK5NX43PYZ4SNHGZ
