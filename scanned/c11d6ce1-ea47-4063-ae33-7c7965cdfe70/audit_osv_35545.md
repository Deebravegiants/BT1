# [M] Hugo 0.91.0 through 0.165.0 Server-Side Request Forgery via security.http.urls Lacking Destination Address Validation

## Summary
Severity: Medium
Advisory: CVE-2026-10582
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-10582
Type: osv

## Details
Hugo's security.http.urls allowlist is the only control on outbound fetches made by resources.GetRemote, and it inspects the URL text alone. CheckAllowedHTTPURL in config/security/securityConfig.go applies the configured pattern list and then re-checks a canonicalised form of an integer, hex or octal IPv4 host, but it never resolves the hostname and never inspects the address the HTTP client actually connects to. The client constructed in resources/resource_factories/create/create.go installs no dial-time hook, so no check occurs at connection time either. A hostname that resolves to a loopback, private or cloud-metadata address therefore satisfies the policy, and the response body is embedded in the generated site. An attacker who can supply a URL through content, for example a front-matter field or a CMS field, can make the build fetch an internal endpoint and publish the response in the static output, so the build artifact itself carries the data out.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10582.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-10582
- https://www.vulncheck.com/advisories/hugo-through-server-side-request-forgery-via-security-http-urls-lacking-destination-address-validation
- https://github.com/gohugoio/hugo
- https://github.com/gohugoio/hugo/blob/v0.165.0/config/security/securityConfig.go
- https://github.com/gohugoio/hugo/blob/v0.165.0/resources/resource_factories/create/create.go
