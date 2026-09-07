# [M] Rekor affected by Server-Side Request Forgery (SSRF) via provided public key URL

## Summary
Severity: Medium
Advisory: GHSA-4c4x-jm2x-pf9j
CVE: CVE-2026-24117
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-01-22
Source: https://github.com/advisories/GHSA-4c4x-jm2x-pf9j
Type: github-advisory

## Affected
- Go: `github.com/sigstore/rekor` — affected >=0 <1.5.0

## Details
## Summary

`/api/v1/index/retrieve` supports retrieving a public key via a user-provided URL, allowing attackers to trigger SSRF to arbitrary internal services.

Since the SSRF only can trigger GET requests, the request cannot mutate state. The response from the GET request is not returned to the caller so data exfiltration is not possible. A malicious actor could attempt to probe an internal network through [Blind SSRF](https://portswigger.net/web-security/ssrf/blind).

## Impact

* SSRF to cloud metadata (169.254.169.254)
* SSRF to internal Kubernetes APIs
* SSRF to any service accessible from Fulcio's network

## Patches

Upgrade to v1.5.0. Note that this is a breaking change to the search API and fully disables lookups by URL. If you require this feature, please reach out and we can discuss alternatives.

## Workarounds

Disable the search endpoint with `--enable_retrieve_api=false`.

## References
- https://github.com/sigstore/rekor/security/advisories/GHSA-4c4x-jm2x-pf9j
- https://nvd.nist.gov/vuln/detail/CVE-2026-24117
- https://github.com/sigstore/rekor/commit/60ef2bceba192c5bf9327d003bceea8bf1f8275f
- https://github.com/sigstore/rekor
- https://github.com/sigstore/rekor/releases/tag/v1.5.0
