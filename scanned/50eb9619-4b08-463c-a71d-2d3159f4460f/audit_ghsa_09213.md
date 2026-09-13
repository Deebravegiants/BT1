# [M] Bunsink has an SSRF bypass in `validate_webhook_url`

## Summary
Severity: Medium
Advisory: GHSA-fp53-qcf8-2xx2
CVE: CVE-2026-44502
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-fp53-qcf8-2xx2
Type: github-advisory

## Affected
- PyPI: `bugsink` — affected >=0 <2.1.3

## Details
## Summary

Bugsink’s webhook URL validation in versions 2.1.2 and earlier could be (partially) bypassed because of a mismatch in URL parsing.

In some malformed URLs, Python’s standard URL  parser (urllib) and the HTTP client stack (requests / urllib3) do not agree on which host is actually being targeted. That could allow a webhook URL to pass Bugsink’s outbound-host checks while the actual HTTP request is sent somewhere else.

## Impact

This issue affects Bugsink’s outbound webhook integrations.

An attacker who can supply or influence a webhook URL may be able to make Bugsink send an outbound HTTP POST request to a host that should have been blocked by the webhook validation logic, including loopback,
private, or otherwise non-allowlisted destinations.

The practical impact is limited:

- this is an outbound webhook SSRF issue, not a general-purpose proxy
- Bugsink does not follow redirects for these webhook requests
- the request shape is constrained by how the malformed URL is normalized by the HTTP client
- this does not give arbitrary control over every possible request path

In other words, this is a real validation bypass, but it is narrower than a full arbitrary-request primitive.

## Technical Details

The original validation logic parsed webhook URLs with Python’s urllib.parse.urlparse, then sent the request with requests.post.

For malformed inputs involving backslashes and @, those components can disagree about where the authority ends and which hostname is the real target. A URL may therefore appear to target an allowlisted public
hostname during validation, while the HTTP client actually connects to a different host.

## Fix

The fix has two parts:

1. Bugsink now normalizes webhook URLs using the same HTTP client stack that will later send them, and applies validation to that normalized form.
2. Bugsink now outright rejects raw webhook URLs containing characters outside the RFC URL character set, rather than relying on downstream normalization of malformed input.

Together, these changes remove the parser discrepancy and make webhook URL handling stricter and more predictable.

## Workarounds

If users cannot upgrade immediately:

- restrict who can configure or modify webhook URLs
- review existing webhook configurations for malformed or unusual URLs
- prefer tightly controlled outbound network policy at the deployment level

## References
- https://github.com/bugsink/bugsink/security/advisories/GHSA-fp53-qcf8-2xx2
- https://nvd.nist.gov/vuln/detail/CVE-2026-44502
- https://github.com/bugsink/bugsink/commit/940d2df635e06803ef658666d734306942db5cc7
- https://github.com/bugsink/bugsink
- https://github.com/bugsink/bugsink/releases/tag/2.1.3
