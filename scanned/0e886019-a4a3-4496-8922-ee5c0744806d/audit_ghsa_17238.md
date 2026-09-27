# [H] Sigstore Timestamp Authority allocates excessive memory during request parsing

## Summary
Severity: High
Advisory: GHSA-4qg8-fj49-pxjh
CVE: CVE-2025-66564
CWE: CWE-405
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-12-05
Source: https://github.com/advisories/GHSA-4qg8-fj49-pxjh
Type: github-advisory

## Affected
- Go: `github.com/sigstore/timestamp-authority` — affected >=0 <2.0.3

## Details
### Impact

**Excessive memory allocation**

Function [api.ParseJSONRequest](https://github.com/sigstore/timestamp-authority/blob/26d7d426d3000abdbdf2df34de56bb92246c0365/pkg/api/timestamp.go#L63) currently splits (via a call to [strings.Split](https://pkg.go.dev/strings#Split)) an optionally-provided OID (which is untrusted data) on periods. Similarly, function [api.getContentType](https://github.com/sigstore/timestamp-authority/blob/26d7d426d3000abdbdf2df34de56bb92246c0365/pkg/api/timestamp.go#L114) splits the `Content-Type` header (which is also untrusted data) on an `application` string.

As a result, in the face of a malicious request with either an excessively long OID in the payload containing many period characters or a malformed `Content-Type` header, a call to `api.ParseJSONRequest` or `api.getContentType` incurs allocations of O(n) bytes (where n stands for the length of the function's argument). Relevant weakness: [CWE-405: Asymmetric Resource Consumption (Amplification)](https://cwe.mitre.org/data/definitions/405.html)

### Patches

Upgrade to v2.0.3.

### Workarounds

There are no workarounds with the service itself. If the service is behind a load balancer, configure the load balancer to reject excessively large requests.

## References
- https://github.com/sigstore/timestamp-authority/security/advisories/GHSA-4qg8-fj49-pxjh
- https://nvd.nist.gov/vuln/detail/CVE-2025-66564
- https://github.com/sigstore/timestamp-authority/commit/0cae34e197d685a14904e0bad135b89d13b69421
- https://github.com/sigstore/timestamp-authority
