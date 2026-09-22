# [H] Fulcio allocates excessive memory during token parsing

## Summary
Severity: High
Advisory: GHSA-f83f-xpx7-ffpw
CVE: CVE-2025-66506
CWE: CWE-405
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-12-05
Source: https://github.com/advisories/GHSA-f83f-xpx7-ffpw
Type: github-advisory

## Affected
- Go: `github.com/sigstore/fulcio` — affected >=0 <1.8.3

## Details
Function [identity.extractIssuerURL](https://github.com/sigstore/fulcio/blob/main/pkg/identity/issuerpool.go#L44-L45) currently splits (via a call to [strings.Split](https://pkg.go.dev/strings#Split)) its argument (which is untrusted data) on periods.

As a result, in the face of a malicious request with an (invalid) OIDC identity token in the payload containing many period characters, a call to `extractIssuerURL` incurs allocations to the tune of O(n) bytes (where n stands for the length of the function's argument), with a constant factor of about 16. Relevant weakness: [CWE-405: Asymmetric Resource Consumption (Amplification)](https://cwe.mitre.org/data/definitions/405.html)

Details
See [identity.extractIssuerURL](https://github.com/sigstore/fulcio/blob/main/pkg/identity/issuerpool.go#L44-L45)

Impact
Excessive memory allocation

## References
- https://github.com/sigstore/fulcio/security/advisories/GHSA-f83f-xpx7-ffpw
- https://nvd.nist.gov/vuln/detail/CVE-2025-66506
- https://github.com/sigstore/fulcio/commit/765a0e57608b9ef390e1eeeea8595b9054c63a5a
- https://github.com/sigstore/fulcio
