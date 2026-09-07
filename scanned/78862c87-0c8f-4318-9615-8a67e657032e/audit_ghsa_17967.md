# [M] github.com/gorilla/csrf improperly validates TrustedOrigins allowing CSRF attacks

## Summary
Severity: Medium
Advisory: GHSA-82ff-hg59-8x73
CVE: CVE-2025-47909
CWE: CWE-352, CWE-807
Ecosystem: Go
CVSS: CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-08-29
Source: https://github.com/advisories/GHSA-82ff-hg59-8x73
Type: github-advisory

## Affected
- Go: `github.com/gorilla/csrf` — affected >=0

## Details
Hosts listed in TrustedOrigins implicitly allow requests from the corresponding HTTP origins, allowing network MitMs to perform CSRF attacks.

After the CVE-2025-24358 fix, a network attacker that places a form at http://example.com can't get it to submit to https://example.com because the Origin header is checked with sameOrigin against a synthetic URL.

However, if a host is added to TrustedOrigins, both its HTTP and HTTPS origins will be allowed, because the schema of the synthetic URL is ignored and only the host is checked. For example, if an application is hosted on https://example.com and adds example.net to TrustedOrigins, a network attacker can serve a form at http://example.net to perform the attack.

Applications should migrate to net/http.CrossOriginProtection, introduced in Go 1.25. If that is not an option, a backport is available as a module at filippo.io/csrf, and a drop-in replacement for the github.com/gorilla/csrf API is available at filippo.io/csrf/gorilla.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-47909
- https://github.com/golang/vulndb/issues/3884
- https://github.com/gorilla/csrf
- https://pkg.go.dev/vuln/GO-2025-3884
